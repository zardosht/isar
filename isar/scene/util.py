import math
from typing import NamedTuple
import numpy as np

from PyQt5.QtGui import QImage, QPixmap

class RefFrame(NamedTuple):
    x: float
    y: float
    width: float
    height: float


class Frame(NamedTuple):
    width: int
    height: int


def is_valid_name(name):
    if len(name) == 0:
        return False
    is_valid = False
    is_valid = all(c.isalnum() or
                   c.isspace() or
                   c == "-" or
                   c == "_"
                   for c in name)
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
    x_scale = image_size.width / camera_view_size.width
    y_scale = image_size.height / camera_view_size.height
    return int(x * x_scale), int(y * y_scale)


def convert_object_to_image(point, phys_obj):
    if phys_obj is None:
        return point

    object_frame = phys_obj.ref_frame
    if phys_obj.is_tracking() and phys_obj.pose_estimation is not None:
        homogenous_position = np.array((point[0], point[1], 1)).reshape((3, 1))
        new_position = np.dot(phys_obj.pose_estimation.homography, homogenous_position)
        return new_position[0] + object_frame.x, new_position[1] + object_frame.y
    else:
        return point[0] + object_frame.x, point[1] + object_frame.y


def convert_image_to_object(point, object_frame:RefFrame):
    if object_frame is None:
        return point

    return point[0] - object_frame.x, point[1] - object_frame.y


def intersects_with_phys_obj(point, phys_obj):
    obj_frame = phys_obj.ref_frame
    return obj_frame.x <= point[0] <= obj_frame.x + obj_frame.width and \
           obj_frame.y <= point[1] <= obj_frame.y + obj_frame.height


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




