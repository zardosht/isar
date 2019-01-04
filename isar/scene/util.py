import math
from typing import NamedTuple

from PyQt5.QtGui import QImage, QPixmap


class RefFrame(NamedTuple):
    x: float
    y: float
    width: float
    height: float


class ImageFrame(NamedTuple):
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


def relative_coordinates_to_image_coordinates(img_frame, rel_x, rel_y, ref_frame=None):
    # based on the scale factor between opencv image size and
    # the camera_view image size
    if ref_frame is not None:
        ref_frame_img_x, ref_frame_img_y = relative_coordinates_to_image_coordinates(img_frame, ref_frame.x, ref_frame.y)

        ref_frame_img_width, ref_frame_img_height = \
            relative_coordinates_to_image_coordinates(img_frame, ref_frame.width, ref_frame.height)

        abs_x_in_ref_frame, abs_y_in_ref_frame = relative_coordinates_to_image_coordinates(
            ImageFrame(ref_frame_img_width, ref_frame_img_height), rel_x, rel_y)

        img_x = ref_frame_img_x + abs_x_in_ref_frame
        img_y = ref_frame_img_y + abs_y_in_ref_frame

    else:
        img_x = int(rel_x * img_frame.width)
        img_y = int(rel_y * img_frame.height)

    return img_x, img_y


def relative_distance_to_image_coordinates(image_frame, rel_distance):
    # based on the scale factor between opencv image size and
    # the camera_view image size
    # opencv_img_shape[1] is width
    img_dist = int(rel_distance * image_frame.width)
    return int(img_dist)


def image_coordinates_to_relative_coordinates(image_frame, x, y):
    return x / image_frame.width, y / image_frame.height








