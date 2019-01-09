import math
from typing import NamedTuple

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


def get_point_in_ref_frame(point, ref_frame:RefFrame):
    if ref_frame is None:
        return point

    return point[0] + ref_frame.x, point[1] + ref_frame.y








