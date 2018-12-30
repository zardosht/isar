import random
import numpy as np
import cv2

from isar.scene import util
from isar.scene.physicalobjectmodel import PhysicalObject


colors = [tuple(255 * np.random.rand(3)) for i in range(10)]


def draw_physical_object_image(opencv_img, phys_obj: PhysicalObject):
    height, width, _ = phys_obj.template_image.shape
    rel_x, rel_y = phys_obj.scene_position
    x, y = util.relative_coordinates_to_image_coordinates(opencv_img.shape, rel_x, rel_y)
    opencv_img[y:y + height, x:x + width] = phys_obj.template_image


def draw_physical_object_bounding_box(opencv_img, phys_obj: PhysicalObject):
    color = random.choice(colors)
    text = '{}: {:.0f}%'.format(phys_obj.name, phys_obj.detection_confidence * 100)
    opencv_img = cv2.rectangle(opencv_img, phys_obj.top_left, phys_obj.bottom_right, color, 2)
    cv2.putText(opencv_img, text, phys_obj.top_left, cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 0), 1)


