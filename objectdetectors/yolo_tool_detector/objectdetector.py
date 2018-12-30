import logging
import time

from isar.tracking.objectdetection import ObjectDetectionPrediction
from objectdetectors.yolo_tool_detector import physical_objects

logger = logging.getLogger("isar.objectdetectors.yolo_simple_tool_detector")

name = "YOLO_SIMPLE_TOOL_DETECTOR"
description = "Yolo simple tool detector"


def get_predictions(frame):
    # TODO: get predictions from YOLO
    # prediction_results = tfnet.return_predict(frame)

    # prediction_results = []
    #
    # predictions = []
    # for pred_result in prediction_results:
    #     tl = (pred_result['topleft']['x'], pred_result['topleft']['y'])
    #     br = (pred_result['bottomright']['x'], pred_result['bottomright']['y'])
    #     label = pred_result['label']
    #     confidnece = pred_result['confidence']
    #     predictions.append(ObjectDetectionPrediction(label, confidnece, tl, br))

    time.sleep(1)
    predictions = []
    predictions.append(ObjectDetectionPrediction("Pump Pliers", 0.8, (50, 70), (100, 120)))
    return predictions


def get_physical_objects():
    return physical_objects


if __name__ == "__main__":
    print(get_physical_objects())


