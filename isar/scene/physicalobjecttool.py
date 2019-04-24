import logging
import math
import random
import numpy as np
import cv2

from isar.scene import sceneutil
from isar.scene.physicalobjectmodel import PhysicalObject


logger = logging.getLogger("isar.scene.physicalobjecttool")

colors = [tuple(255 * np.random.rand(3)) for i in range(10)]


def draw_physical_object_image(opencv_img, scene_scale_factor, phys_obj: PhysicalObject):
    template_image = phys_obj.template_image
    template_image_scaled = cv2.resize(template_image, dsize=(0, 0), fx=scene_scale_factor[0], fy=scene_scale_factor[1])
    sceneutil.draw_image_on(opencv_img, template_image_scaled, phys_obj.scene_position, position_is_topleft=True)


def draw_physical_object_bounding_box(opencv_img, scene_rect, phys_obj: PhysicalObject):
    color = random.choice(colors)
    text = '{}: {:.0f}%'.format(phys_obj.name, phys_obj.detection_confidence * 100)

    tl = (phys_obj.top_left[0] - scene_rect[0], phys_obj.top_left[1] - scene_rect[1])
    br = (phys_obj.bottom_right[0] - scene_rect[0] , phys_obj.bottom_right[1] - scene_rect[1])
    opencv_img = cv2.rectangle(opencv_img, tl, br, color, 2)
    cv2.putText(opencv_img, text, tl, cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 0), 1)

