import logging
import random
import numpy as np
import cv2

from isar.scene import sceneutil
from isar.scene.physicalobjectmodel import PhysicalObject


logger = logging.getLogger("isar.scene.physicalobjecttool")

colors = [tuple(255 * np.random.rand(3)) for i in range(10)]

scaled_phys_obj_images = {}


def draw_physical_object_image(opencv_img, scene_scale_factor, phys_obj: PhysicalObject):
    global scaled_phys_obj_images
    template_image_scaled = scaled_phys_obj_images.get(phys_obj.name)
    if template_image_scaled is None:
        template_image = phys_obj.template_image
        template_image_scaled = cv2.resize(template_image, dsize=(0, 0), fx=scene_scale_factor[0], fy=scene_scale_factor[1])
        add_red_cross(template_image_scaled)
        scaled_phys_obj_images[phys_obj.name] = template_image_scaled

    sceneutil.draw_image_on(opencv_img, template_image_scaled, phys_obj.scene_position, position_is_topleft=True)
    if phys_obj.highlight:
        highlight_physical_object(opencv_img,
                                  phys_obj.scene_position,
                                  (template_image_scaled.shape[1], template_image_scaled.shape[0]),
                                  phys_obj.highlight_color)


def draw_physical_object_bounding_box(opencv_img, phys_obj: PhysicalObject):
    color = random.choice(colors)
    if phys_obj.detection_confidence is not None:
        text = '{}: {:.0f}%'.format(phys_obj.name, phys_obj.detection_confidence * 100)
    else:
        text = '{}'.format(phys_obj.name)

    ref_frame = phys_obj.ref_frame
    if ref_frame is None:
        logger.warning("phy_obj.ref_frame is None. Return.")
        return

    tl = (ref_frame.x, ref_frame.y)
    br = ((ref_frame.x + ref_frame.width), (ref_frame.y + ref_frame.height))
    opencv_img = cv2.rectangle(opencv_img, tl, br, color, 1)
    cv2.putText(opencv_img, text, tl, cv2.FONT_HERSHEY_COMPLEX, .5, (0, 0, 0), 1)
    if phys_obj.highlight:
        highlight_physical_object(opencv_img, tl, (ref_frame.width, ref_frame.height), phys_obj.highlight_color)


def highlight_physical_object(opencv_img, position, size, color):
    br = (position[0] + size[0], position[1] + size[1])
    cv2.rectangle(opencv_img, position, br, color, 5)


def add_red_cross(phys_obj_template_image):
    # If pyhsical object is not available on the scene,
    # its template image is drawn with a red cross.
    # This has two reasons:
    # 1) YOLO does not detect mistakenly the template image as the real object
    # 2) Red cross indicated the object is missing
    height, width = phys_obj_template_image.shape[0:2]
    color = (0, 0, 255)
    thickness = 5
    p1 = (0, 0)
    p2 = (width - 1, height -1)
    template_image = cv2.line(phys_obj_template_image, p1, p2, color, thickness)
    p1 = (0, height - 1)
    p2 = (width - 1, 0)
    template_image = cv2.line(phys_obj_template_image, p1, p2, color, thickness)
    return template_image