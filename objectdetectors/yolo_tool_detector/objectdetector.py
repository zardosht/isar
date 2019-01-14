import cv2
import logging
import os
import time
import traceback

from isar.camera.camera import CameraFrame
from isar.tracking.objectdetection import ObjectDetectionPrediction
from objectdetectors.yolo_tool_detector import physical_objects, object_detector_package_path, temp_folder_path, \
    physical_objects_dict

import multiprocessing as mp

from objectdetectors.yolo_tool_detector.poseestimation import PoseEstimator, PoseEstimationInput

logger = logging.getLogger("isar.objectdetectors.yolo_simple_tool_detector.detector")

name = "YOLO_SIMPLE_TOOL_DETECTOR"
description = "Yolo simple tool detector"

activate = True

debug = False

tfnet = None
pose_estimators = []

best_homographies = {}
pose_estimation_task_queue = mp.JoinableQueue()
pose_estimation_results_queue = mp.Queue()


def get_predictions(frame: CameraFrame):
    # feed the video/camera_feed into Yolo and get the bounding boxes of detected objects
    # crop the detected objects from Yolo output frame
    # find the corresponding object in the list of saved domain objects
    # for each saved object find features in the reference image and in the matching cropped image
    # use matcher to match the features
    # compute the homography from the set of matched features
    # apply homograph to the position of the annotations.
    if tfnet is None:
        init_yolo()
        logger.info("YOLO model loaded.")

    predictions = []
    try:
        if len(pose_estimators) == 0:
            init_pose_estimators()

        # To make object detection faster we can resize the frame if needed.
        # However, we should calculate back the coordinates returned by object detector based on the scale factor.

        t1 = time.time()
        predictions = run_object_detection(frame)
        estimate_pose(predictions)

    except Exception as e:
        logging.error(e)
        traceback.print_tb(e.__traceback__)

    logger.info("Object detections and computing homographies took {}".format(time.time() - t1))
    return predictions


def estimate_pose(predictions):
    physical_object_names = [prediction.label for prediction in predictions]
    remove_from_best_homographies = list(set(best_homographies.keys()) - set(physical_object_names))
    for name in remove_from_best_homographies:
        del best_homographies[name]

    for target in predictions:
        template = physical_objects_dict[target.label]
        best_homography = None
        if template.name in best_homographies and \
                best_homographies[template.name] is not None:
            best_homography = best_homographies[template.name]

        pe_input = PoseEstimationInput(template.name, template.template_image, target.image, best_homography)
        pose_estimation_task_queue.put(pe_input)

    pose_estimation_task_queue.join()
    for i in range(len(physical_objects)):
        if not pose_estimation_results_queue.empty():
            pe_output = pose_estimation_results_queue.get()
            best_homographies[pe_output.object_name] = pe_output

    for prediction in predictions:
        prediction.pose_estimation = best_homographies[prediction.label]


def run_object_detection(frame: CameraFrame):
    predictions = []
    try:
        if tfnet is None:
            init_yolo()

        prediction_results = tfnet.return_predict(frame.raw_image)
        for pred_result in prediction_results:
            tl = (pred_result['topleft']['x'], pred_result['topleft']['y'])
            br = (pred_result['bottomright']['x'], pred_result['bottomright']['y'])
            label = pred_result['label']
            confidence = pred_result['confidence']
            prediction = ObjectDetectionPrediction(label, confidence, tl, br, frame.size)
            prediction.image = frame.raw_image[tl[1]:br[1], tl[0]:br[0]].copy()
            if debug:
                cv2.imwrite(str(os.path.join(temp_folder_path, label + "_prediciton.jpg")), prediction.image)
            # prediction.homography = will be set in the get_predictions
            predictions.append(prediction)
    except Exception as e:
        logging.error(e)
        traceback.print_tb(e.__traceback__)

    return predictions


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


def init_pose_estimators():
    global pose_estimators
    num_processes = 10
    pose_estimators = [PoseEstimator(pose_estimation_task_queue, pose_estimation_results_queue) for i in range(num_processes)]
    for p in pose_estimators:
        p.start()

    logger.info("All pose estimator processes started.")


def terminate():
    for pose_estimator in pose_estimators:
        pose_estimator.terminate()


def get_physical_objects():
    return physical_objects


def run_mock_obj_detection():
    # if tfnet is None:
    #     init_yolo()
    #
    # x, y = 300, 200
    # width, height = 160, 380
    #
    # time.sleep(1)
    # predictions = [ObjectDetectionPrediction("Pump Pliers", 0.8, (x, y), (x + width, y + height), frame.size)]
    # return predictions
    pass


if __name__ == "__main__":
    print(get_physical_objects())



