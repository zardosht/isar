import os

import cv2
import logging
import time

from isar.tracking.objectdetection import ObjectDetectionPrediction
from objectdetectors.dummy_detector import physical_objects, temp_folder_path

logger = logging.getLogger("isar.objectdetectors.dummy_detector")

activate = False

name = "DUMMY_DETECTOR"
description = "Dummy detector"


def get_predictions(frame):
    ## TODO: Remove. Dummy test code
    # x += 10
    # if x > frame.size[0]: x = 0
    # y += 10
    # if y > frame.size[1]: y = 0

    # TODO: Remove. Dummy test code
    x, y = 100, 100
    width, height = 100, 100

    time.sleep(1)
    predictions = []
    tl = (x, y)
    br = (x + width, y + height)
    prediction = ObjectDetectionPrediction("Rubber Duck", 0.8, tl, br, frame.size)
    prediction.image = frame.raw_image[tl[1]:br[1], tl[0]:br[0]].copy()
    cv2.imwrite(str(os.path.join(temp_folder_path, "dummy_prediciton_image.jpg")), prediction.image)
    predictions.append(prediction)
    return predictions


def get_physical_objects():
    return physical_objects


if __name__ == "__main__":
    print(get_physical_objects())


