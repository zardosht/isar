from ast import literal_eval

import cv2
import logging
import math
import traceback
from typing import NamedTuple
import numpy as np

from PyQt5.QtGui import QImage, QPixmap

import isar
from isar import ApplicationMode

logger = logging.getLogger("isar.scene.util")

aruco_dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

scene_rect_c = None
scene_rect_p = None
scene_scale_factor_c = None
scene_scale_factor_p = None
scene_scale_factor = None
cam_proj_homography = None


ANNOTATION_ID_SEPARATOR = "."

SCENE_TOP_LEFT_MARKER_ID = 0
SCENE_BOTTOM_RIGHT_MARKER_ID = 1


class RefFrame(NamedTuple):
    x: float
    y: float
    width: float
    height: float


class Frame(NamedTuple):
    width: int
    height: int


def is_valid_name(name, taken_names=None):
    if len(name) == 0:
        return False
    is_valid = False
    is_valid = all(c.isalnum() or
                   c.isspace() or
                   c == "-" or
                   c == "_"
                   for c in name)
    if name in taken_names:
        is_valid = False

    return is_valid


def calc_distance(p1, p2):
    if p1 is None:
        return None

    if p2 is None:
        return None

    return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))


def calc_rect_area(vertex1, vertex2):
    if vertex1 is None:
        return None

    if vertex2 is None:
        return None

    width = math.fabs(vertex1[0] - vertex2[0])
    height = math.fabs(vertex1[1] - vertex2[1])

    return width * height


def get_pixmap_from_np_image(np_image):
    qimg = get_qimage_from_np_image(np_image)
    return QPixmap.fromImage(qimg)


def get_qimage_from_np_image(np_image):
    qfromat = QImage.Format_Indexed8
    if len(np_image.shape) == 3:  # sahpe[0] = rows, [1] = cols, [2] = channels
        if np_image.shape[2] == 4:
            qfromat = QImage.Format_RGBA8888
        else:
            qfromat = QImage.Format_RGB888

    out_image = QImage(np_image,
                       np_image.shape[1], np_image.shape[0],
                       np_image.strides[0], qfromat)
    out_image = out_image.rgbSwapped()
    return out_image


def mouse_coordinates_to_image_coordinates(x, y, camera_view_size, image_size):
    if image_size is None:
        return x, y

    x_scale = image_size.width / camera_view_size.width
    y_scale = image_size.height / camera_view_size.height
    return int(x * x_scale), int(y * y_scale)


def convert_object_to_image(point, phys_obj, scene_scale_factor=(1., 1.)):
    if phys_obj is None:
        return point

    if point is None:
        return point

    if scene_scale_factor is None:
        scene_scale_factor = (1., 1.)

    object_frame = phys_obj.ref_frame
    if phys_obj.is_tracking() and phys_obj.pose_estimation is not None:
        homogenous_position = np.array((point[0], point[1], 1)).reshape((3, 1))
        new_position = np.dot(phys_obj.pose_estimation.homography, homogenous_position)
        return new_position[0] + object_frame.x, new_position[1] + object_frame.y
    else:
        return int((point[0] * scene_scale_factor[0]) + object_frame.x), \
               int((point[1] * scene_scale_factor[1]) + object_frame.y)


def convert_image_to_object(point, object_frame:RefFrame, scene_scale_factor=(1., 1.)):
    if object_frame is None:
        return point

    return int((point[0] - object_frame.x) * (1 / scene_scale_factor[0])), \
        int((point[1] - object_frame.y) * (1 / scene_scale_factor[1]))


def get_left2right_topdown(v1, v2):
    width = v2[0] - v1[0]
    left_to_right = False
    if width >= 0:
        left_to_right = True

    height = v2[1] - v1[1]
    topdown = False
    if height >= 0:
        bottom_up = True

    return left_to_right, topdown


def flip_image(img, flip_x=False, flip_y=False, copy=False):
    # flipCode	a flag to specify how to flip the array;
    # 0 means flipping around the x-axis and
    # positive value (for example, 1) means flipping around y-axis.
    # Negative value (for example, -1) means flipping around both axes.
    result = img
    if copy:
        result = img.copy()

    if flip_x:
        result = cv2.flip(result, 0)

    if flip_y:
        result = cv2.flip(result, 1)

    return result


def draw_image_on(opencv_img, overlay_img, position, position_is_topleft=True, position_is_bottom_left=False):
    try:
        overlay_img_height, overlay_img_width, _ = overlay_img.shape
        scene_height, scene_width, _ = opencv_img.shape

        # TODO: check that the position is not out of opencv_img bounds
        if position_is_topleft:
            x, y = position
        elif position_is_bottom_left:
            x = position[0]
            y = position[1] - overlay_img_height
        else:
            # position is center
            x = position[0] - math.floor(overlay_img_width / 2)
            y = position[1] - math.floor(overlay_img_height / 2)

        # check that the position is not out of opencv_img bounds
        if x > scene_width or x < 0:
            return
        if y > scene_height or y < 0:
            return

        end_height_index = min(y + overlay_img_height, scene_height)
        end_width_index = min(x + overlay_img_width, scene_width)

        cropped_height = min(overlay_img_height, scene_height - y)
        cropped_width = min(overlay_img_width, scene_width - x)

        opencv_img[y:end_height_index, x:end_width_index] = overlay_img[0:cropped_height, 0:cropped_width]
    except Exception as exp:
        logger.error("Could not draw overlay image.")
        logger.error(exp)
        traceback.print_tb(exp.__traceback__)


def compute_scene_rect(camera_frame, cam_proj_homography=None):
    camera_img = camera_frame.raw_image
    # Detect the scene border markers and get the scene boudaries from them.
    # All scene images must be resized to scene boundaries and shown in the center of projector widget
    marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(camera_img, aruco_dictionary)
    if marker_corners is None or marker_ids is None:
        logger.warning("marker_corners or marker_ids is None. Return.")
        return None, None, None

    # there are only two markers. So, one has index 0, the other has index 1,
    # however we don't know which one is marker 0 (the marker with id 0 must be placed physically at the top-left)
    top_left_marker_index = -1   # that's the marker with id 0
    bottom_right_marker_index = -1  # that's the marker with id 1
    for idx, marker_id in enumerate(marker_ids):
        if marker_id == SCENE_TOP_LEFT_MARKER_ID:
            top_left_marker_index = idx
        if marker_id == SCENE_BOTTOM_RIGHT_MARKER_ID:
            bottom_right_marker_index = idx

    if top_left_marker_index == -1 or bottom_right_marker_index == -1:
        logger.warning("Error detecting the scene corners. Not all two markers were detected. return.")
        return None, None, None

    vertex1_marker = marker_corners[top_left_marker_index].reshape(4, 2)
    vertex2_marker = marker_corners[bottom_right_marker_index].reshape(4, 2)

    # marker corners are in clock-wise order
    # find coordinates of top-left (0) corner of marker 0 and bottom-right (2) corner of marker 1
    c_v1 = (vertex1_marker[0][0], vertex1_marker[0][1])
    c_v2 = (vertex2_marker[2][0], vertex2_marker[2][1])

    scene_width_c, scene_height_c = (abs(c_v1[0] - c_v2[0]), abs(c_v1[1] - c_v2[1]))
    scene_rect_c = int(c_v1[0]), int(c_v1[1]), int(scene_width_c), int(scene_height_c)

    if cam_proj_homography is not None:
        proj_points = cv2.perspectiveTransform(np.array([[c_v1, c_v2]]), cam_proj_homography)
        proj_points = proj_points.squeeze()
        p_v1 = proj_points[0]
        p_v2 = proj_points[1]
        scene_width_p, scene_height_p = (abs(p_v1[0] - p_v2[0]), abs(p_v1[1] - p_v2[1]))

        scene_homography = compute_scene_homography(vertex1_marker, vertex2_marker, cam_proj_homography, camera_img)
        scene_rect_p = int(p_v1[0]), int(p_v1[1]), int(scene_width_p), int(scene_height_p)

        return scene_rect_c, scene_rect_p, scene_homography
    else:

        return scene_rect_c, None, None


def compute_scene_homography(v1_marker, v2_marker, cam_proj_homography, camera_img):
    # I tried also to calculate the scene homography with more points. But it didn't change the results:
    # the scene projected on the table is still rotated. I don't use this scene homography.

    v1_marker_normalized = v1_marker - v1_marker[0]
    v2_marker_normalized = v2_marker - v1_marker[0]

    v1_marker_p = cv2.perspectiveTransform(np.array([v1_marker]), cam_proj_homography).squeeze()
    v2_marker_p = cv2.perspectiveTransform(np.array([v2_marker]), cam_proj_homography).squeeze()

    v1_marker_p_normalized = v1_marker_p - v1_marker_p[0]
    v2_marker_p_normalized = v2_marker_p - v1_marker_p[0]

    camera_points = np.vstack((v1_marker_normalized, v2_marker_normalized))
    projector_points = np.vstack((v1_marker_p_normalized, v2_marker_p_normalized))

    scene_homography, _ = cv2.findHomography(np.array([camera_points]),  np.array([projector_points]), cv2.RANSAC, 3)
    # scene_affine_transform = cv2.getAffineTransform(np.array([camera_points[0:3]]), np.array([projector_points[0:3]]))
    # scene_homography, _ = cv2.findHomography(np.array([projector_points]), np.array([camera_points]), cv2.RANSAC, 3)

    return scene_homography


def get_scene_scale_factor_c(camera_img_shape, scene_rect_c):
    scene_width_c = scene_rect_c[2]
    scene_height_c = scene_rect_c[3]
    camera_img_width = camera_img_shape[1]
    camera_img_height = camera_img_shape[0]
    return scene_width_c / camera_img_width, scene_height_c / camera_img_height


def get_scene_scale_factor_p(projector_img_shape, scene_rect_p):
    scene_width_p = scene_rect_p[2]
    scene_height_p = scene_rect_p[3]
    projector_img_width = projector_img_shape[1]
    projector_img_height = projector_img_shape[0]
    return scene_width_p / projector_img_width, scene_height_p / projector_img_height


def camera_coord_to_scene_coord(cam_coord, for_projector=False):
    if isar.application_mode == ApplicationMode.AUTHORING:
        return camera_coord_to_scene_coord_c(cam_coord)
    elif isar.application_mode == ApplicationMode.EXECUTION:
        if scene_rect_c is None:
            return cam_coord

        if scene_rect_p is None:
            return cam_coord

        cam_to_scene_coord = camera_coord_to_scene_coord_c(cam_coord)
        if for_projector:
            sf = (scene_rect_p[2] / scene_rect_c[2], scene_rect_p[3] / scene_rect_c[3])
            cam_to_scene_coord = int(cam_to_scene_coord[0] * sf[0]), int(cam_to_scene_coord[1] * sf[1])

        return cam_to_scene_coord

        # return camera_coord_to_scene_coord_p(cam_coord)


def camera_coord_to_scene_coord_c(cam_coord):
    if scene_rect_c is None:
        return cam_coord

    if cam_coord is None:
        return cam_coord

    return cam_coord[0] - scene_rect_c[0], cam_coord[1] - scene_rect_c[1]


def camera_coord_to_scene_coord_p(cam_coord):
    if scene_rect_p is None:
        return cam_coord

    if cam_coord is None:
        return cam_coord

    proj_coord = convert_camera_coord_to_porjector_coord(cam_coord)
    return projector_coord_to_scene_coord_p(proj_coord)


def projector_coord_to_scene_coord_p(proj_coord):
    if scene_rect_p is None:
        return proj_coord

    if proj_coord is None:
        return proj_coord

    return proj_coord[0] - scene_rect_p[0], proj_coord[1] - scene_rect_p[1]


def camera_coords_to_scene_coords(cam_coords, for_projector=False):
    result = []
    for cam_coord in cam_coords:
        result.append(camera_coord_to_scene_coord(cam_coord, for_projector))
    return result


def create_empty_image(size, color):
    empty_image = np.ones((size[1], size[0], 3), np.uint8)
    empty_image[:] = color
    return empty_image


def convert_camera_coord_to_porjector_coord(p):
    if p is None:
        return p

    if cam_proj_homography is None:
        return p

    else:
        proj_point = cv2.perspectiveTransform(np.array([[(float(p[0]), float(p[1]))]]), cam_proj_homography).squeeze()
        return int(proj_point[0]), int(proj_point[1])


def get_color_from_str(value):
    literal = get_literal_from_str(value)
    if literal and \
            isinstance(literal, tuple) and \
            len(literal) == 3 and \
            isinstance(literal[0], int) and \
            isinstance(literal[1], int) and \
            isinstance(literal[2], int):
        return literal, True
    else:
        return value, False


def get_literal_from_str(str_val):
    value = None
    if isinstance(str_val, str):
        if str_val == "":
            return value

        try:
            value = literal_eval(str_val)
        except Exception as e:
            logger.error("Error converting value:", e)
        finally:
            return value
