import logging
import time

from isar.tracking.objectdetection import ObjectDetectionPrediction
from objectdetectors.dummy_detector import physical_objects

logger = logging.getLogger("isar.objectdetectors.dummy_detector")

name = "DUMMY_DETECTOR"
description = "Dummy detector"


def get_predictions(frame):
    time.sleep(1)
    predictions = []
    prediction = ObjectDetectionPrediction("Horse", 0.8, (201, 203), (301, 303), frame.size)
    predictions.append(prediction)
    return predictions


def get_physical_objects():
    return physical_objects


if __name__ == "__main__":
    print(get_physical_objects())


