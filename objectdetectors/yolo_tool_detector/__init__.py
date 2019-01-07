import json
import logging
import os
import cv2

from isar.scene.physicalobjectmodel import PhysicalObject


logger = logging.getLogger("isar.objectdetectors.yolo_simple_tool_detector")

object_detector_package_path = os.path.dirname(__file__)

physical_objects = []


def init_physical_objects():
    template_images_path = os.path.join(object_detector_package_path, "template_images/")
    physical_objects_json_path = os.path.join(object_detector_package_path, "physical_objects.json")

    with open(physical_objects_json_path) as f:
        po_dicts = json.load(f)

    for po_dict in po_dicts:
        po = PhysicalObject()
        po.__dict__.update(po_dict)
        po.template_image = cv2.imread(str(template_images_path) + po.image_path)
        physical_objects.append(po)


init_physical_objects()










