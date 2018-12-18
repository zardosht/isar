import json
import os
import cv2

from isar.scene.physicalobjectmodel import PhysicalObject


object_detector_package_path = os.path.dirname(__file__)
template_images_path = os.path.join(object_detector_package_path, "template_images/")
physical_objects_json_path = os.path.join(object_detector_package_path, "physical_objects.json")

physical_objects = []
with open(physical_objects_json_path) as f:
    po_dicts = json.load(f)

for po_dict in po_dicts:
    po = PhysicalObject()
    po.__dict__.update(po_dict)
    po.image = cv2.imread(str(template_images_path) + po.image_path)
    physical_objects.append(po)



