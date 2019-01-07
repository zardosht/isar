import logging
import os
import time
import traceback

from isar.camera.camera import CameraFrame
from isar.tracking.objectdetection import ObjectDetectionPrediction
from objectdetectors.yolo_tool_detector import physical_objects, object_detector_package_path

logger = logging.getLogger("isar.objectdetectors.yolo_simple_tool_detector.detector")

name = "YOLO_SIMPLE_TOOL_DETECTOR"
description = "Yolo simple tool detector"

tfnet = None


def get_predictions(frame: CameraFrame):
    predictions = []
    try:
        if tfnet is None:
            init_yolo()

        prediction_results = tfnet.return_predict(frame.raw_image)
        for pred_result in prediction_results:
            tl = (pred_result['topleft']['x'], pred_result['topleft']['y'])
            br = (pred_result['bottomright']['x'], pred_result['bottomright']['y'])
            label = pred_result['label']
            confidnece = pred_result['confidence']
            predictions.append(ObjectDetectionPrediction(label, confidnece, tl, br, frame.size))
    except Exception as e:
        logging.error(e)
        traceback.print_tb(e.__traceback__)

    return predictions


    # x, y = 300, 200
    #
    # time.sleep(1)
    # predictions = []
    # predictions.append(ObjectDetectionPrediction("Pump Pliers", 0.8, (x, y), (x + width, y + height), frame.size))
    # return predictions


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


def get_physical_objects():
    return physical_objects


if __name__ == "__main__":
    print(get_physical_objects())



