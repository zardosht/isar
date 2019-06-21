import importlib
import importlib.util
import logging
import multiprocessing as mp
import os
import sys
import threading
import time
import traceback
from queue import Queue
from typing import List

from isar.services.service import Service

logger = logging.getLogger("isar.objectdetection")

"""
We consider each object detector as a plug-in.
For each object detector we start a worker process with the detector as an attribute.
Each worker process has a task and result queue. 
When the service starts we start all teh object detector worker processes and join them. 
When the service stops we terminate all the worker processes. 
"""

OBJECT_DETECTORS_PATH = "./objectdetectors"

"""
A dictionary with object detector name as key and the list of physical objects
        that this object detector can detect as value.
"""
physical_objects = {}

"""
A dictionary with object detectors names as keys and the corresponding object detector module as value. 
"""
object_detectors = {}

OBJECT_DETECTOR_MODULE_FILENAME = "objectdetector.py"
OBJECT_DETECTOR_MODULE_NAME = "objectdetector"

POISON_PILL = "poison_pill"


def init():
    """
    Search the object detectors plugin directory and populate the object_detectors and physical_objects dictionaries
    :return:
    """
    global object_detectors
    entries = os.listdir(OBJECT_DETECTORS_PATH)
    for path_entry in entries:
        path = os.path.join(OBJECT_DETECTORS_PATH, path_entry)
        if not os.path.isdir(path) or not OBJECT_DETECTOR_MODULE_FILENAME in os.listdir(path):
            continue
        try:
            # TODO: ERROR - can't pickle module objects
            module_path = os.path.join(path, OBJECT_DETECTOR_MODULE_FILENAME)
            spec = importlib.util.spec_from_file_location(OBJECT_DETECTOR_MODULE_NAME, module_path)
            obj_detector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(obj_detector)
            if obj_detector.activate:
                object_detectors[obj_detector.name] = obj_detector
                physical_objects[obj_detector.name] = obj_detector.get_physical_objects()

        except Exception as exp:
            logger.error("Could not load object detector module.")
            logger.error(exp)
            traceback.print_tb(exp.__traceback__)

    # load the modlue,
    # populate the dictionaries
    #
    # add the detectors worker class that inherits from multiprocessing process
    # in the start mthod instantiate the worker processes and give the object detector molude
    # each worker has a task queue and a result queue
    # start the workes and join them
    #
    # add the request queue
    # add the response queue
    #
    # start a thread that waits on the request queue
    # as soon as a request is avaialbe, create multiples of it and and send it to all object objectdetectors task queues
    # join the worker processes
    # wait on the result queue of all worker processes
    #
    # when all the detection results are available create a ObjectDetectionResponse object (it has a dictionary
    #     with the name of the object detector as value and the predictions from that detector as value)
    # and put in the response queue


class ObjectDetectionService(Service):
    def __init__(self, service_name=None):
        super().__init__(service_name)
        self.object_detector_workers = []
        self.observer_threads: List[ObjectDetectionObserverThread] = []

    def start(self):
        """
        Start a process for each of the object detectors.
        :return:
        """
        global object_detectors
        for obj_detector_name in object_detectors:
            request_queue = mp.JoinableQueue()
            response_queue = mp.Queue()
            obj_detector_worker = ObjectDetectorWorker(obj_detector_name, request_queue, response_queue)
            # obj_detector_worker.daemon = False
            self.object_detector_workers.append(obj_detector_worker)
            observer_thread = ObjectDetectionObserverThread(Queue(maxsize=1), obj_detector_worker)
            self.observer_threads.append(observer_thread)

        for worker in self.object_detector_workers:
            worker.start()

        for observer_thread in self.observer_threads:
            observer_thread.start()

    def get_present_objects(self, camera_frame, scene_phys_objs_names, callback=None):
        for observer_thread in self.observer_threads:
            if not observer_thread.request_queue.full():
                observer_thread.request_queue.put(ObjectDetectionRequest(camera_frame, scene_phys_objs_names), block=False)
                observer_thread.callback = callback

    def stop(self):
        for observer_thread in self.observer_threads:
            observer_thread.request_queue.put(POISON_PILL)
            observer_thread.join(timeout=2)

        for obj_detector_worker in self.object_detector_workers:
            obj_detector_worker.shut_down()
            obj_detector_worker.terminate()

    @staticmethod
    def get_physical_objects():
        """
        :return: A dictionary with object detector name as key and the list of physical objects
        that this object detector can detect as value.
        """
        global physical_objects
        return physical_objects


class ObjectDetectionObserverThread(threading.Thread):
    def __init__(self, request_queue, obj_detector_worker, callback=None):
        super().__init__()
        self.request_queue = request_queue
        self.obj_detector_worker = obj_detector_worker
        self.callback = callback

    def run(self):
        self.wait_for_object_detection()

    def wait_for_object_detection(self):
        while True:
            obj_detection_req = self.request_queue.get()
            if obj_detection_req == POISON_PILL:
                self.request_queue.task_done()
                break

            phys_obj_predictions = {}
            self.obj_detector_worker.request_queue.put(obj_detection_req)
            obj_detection_response = self.obj_detector_worker.response_queue.get()
            phys_obj_predictions[obj_detection_response.object_detector_name] = obj_detection_response.predictions
            if self.callback is not None:
                try:
                    self.callback(phys_obj_predictions)
                except Exception as exp:
                    logger.error("Error in calling object detection callback.")
                    logger.error(exp)
                    traceback.print_tb(exp.__traceback__)

            self.request_queue.task_done()


class ObjectDetectionPrediction:
    def __init__(self, label, confidence, top_left, bottom_right, camera_frame_size):
        self.label = label
        self.confidence = confidence
        self.camera_frame_size = camera_frame_size
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.image = None
        self.pose_estimation = None

    @property
    def top_left(self):
        return self._top_left

    @top_left.setter
    def top_left(self, value):
        self._top_left = (value[0], value[1])

    @property
    def bottom_right(self):
        return self._bottom_right

    @bottom_right.setter
    def bottom_right(self, value):
        self._bottom_right = (value[0], value[1])


class ObjectDetectionRequest:
    def __init__(self, camera_frame, scene_phys_objs_names):
        self.camera_frame = camera_frame
        self.scene_physical_objects_names = scene_phys_objs_names


class ObjectDetectionResponse:
    def __init__(self, obj_detector_name, predictions):
        self.object_detector_name = obj_detector_name
        self.predictions = predictions


class ObjectDetectorWorker(mp.Process):
    def __init__(self, object_detector_name, request_queue, response_queue):
        mp.Process.__init__(self)
        self.object_detector = object_detectors[object_detector_name]
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.shut_down_event = mp.Event()

    def run(self):
        while True:
            if self.shut_down_event.is_set():
                logger.info("Shutting down: ", self.object_detector.name)
                self.request_queue.task_done()
                sys.exit(0)

            if not self.request_queue.empty():
                obj_detection_request = self.request_queue.get()
                t1 = time.time()
                obj_detection_predictions = self.object_detector.get_predictions(obj_detection_request)
                self.request_queue.task_done()
                self.response_queue.put(ObjectDetectionResponse(self.object_detector.name, obj_detection_predictions))
                logger.debug("Detection of objects by {} took {}".format(self.object_detector.name, time.time() - t1))

    def shut_down(self):
        self.object_detector.terminate()
        self.shut_down_event.set()
