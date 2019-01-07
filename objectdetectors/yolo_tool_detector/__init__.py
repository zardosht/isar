import json
import logging
import os
import cv2

from isar.scene.physicalobjectmodel import PhysicalObject


logger = logging.getLogger("isar.objectdetectors.yolo_simple_tool_detector")

object_detector_package_path = os.path.dirname(__file__)

physical_objects = []
tfnet = None


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


def init_yolo():
    global tfnet
    yolo_model_path = os.path.join(object_detector_package_path, "model/")
    yolo_options = {
        "model": str(yolo_model_path) + "miras_v2.cfg",
        "load": str(yolo_model_path) + "miras_v2_12600.weights",
        "labels": str(yolo_model_path) + "labels.txt",
        "threshold": 0.5,
        "gpu": 1.0
    }
    from darkflow.net.build import TFNet
    tfnet = TFNet(yolo_options)



init_physical_objects()










