import random
import numpy as np
import cv2

from isar.scene import util
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.util import Frame

colors = [tuple(255 * np.random.rand(3)) for i in range(10)]


def draw_physical_object_image(opencv_img, phys_obj: PhysicalObject):
    ti_height, ti_width, _ = phys_obj.template_image.shape
    scene_height, scene_width, _ = opencv_img.shape
    x, y = phys_obj.scene_position

    end_height_index = min(y + ti_height, scene_height)
    end_width_index = min(x + ti_width, scene_width)

    cropped_height = min(ti_height, scene_height - y)
    cropped_width = min(ti_width, scene_width - x)

    opencv_img[y:end_height_index, x:end_width_index] = phys_obj.template_image[0:cropped_height, 0:cropped_width]


def draw_physical_object_bounding_box(opencv_img, phys_obj: PhysicalObject):
    color = random.choice(colors)
    text = '{}: {:.0f}%'.format(phys_obj.name, phys_obj.detection_confidence * 100)

    tl = phys_obj.top_left
    br = phys_obj.bottom_right
    opencv_img = cv2.rectangle(opencv_img, tl, br, color, 2)
    cv2.putText(opencv_img, text, tl, cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 0), 1)


