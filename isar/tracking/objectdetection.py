import importlib
import logging
import multiprocessing as mp
import os
import threading
import time
import traceback
from queue import Queue, Full

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
            module_path = os.path.join(path, OBJECT_DETECTOR_MODULE_FILENAME)
            spec = importlib.util.spec_from_file_location(OBJECT_DETECTOR_MODULE_NAME, module_path)
            obj_detector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(obj_detector)
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
        self._stop_event = threading.Event()
        self.object_detector_workers = []
        self.observer_thread: threading.Thread = None

    def start(self):
        """
        Start a process for each of the object detectors.
        :return:
        """
        global object_detectors
        for obj_detector_name, obj_detector in object_detectors.items():
            request_queue = mp.JoinableQueue()
            response_queue = mp.Queue()
            obj_detector_worker = ObjectDetectorWorker(obj_detector, request_queue, response_queue)
            self.object_detector_workers.append(obj_detector_worker)

        for worker in self.object_detector_workers:
            worker.start()

        self.observer_thread = threading.Thread(target=self.wait_for_object_detection)
        self.observer_thread.request_queue: Queue = Queue(maxsize=1)
        self.observer_thread.start()

    def wait_for_object_detection(self):
        while not self._stop_event.is_set():
            camera_frame = self.observer_thread.request_queue.get()
            if camera_frame == POISON_PILL:
                self.observer_thread.request_queue.task_done()
                break

            t1 = time.time()
            present_objects = {}
            for obj_detector_worker in self.object_detector_workers:
                obj_detector_worker.request_queue.put(ObjectDetectionRequest(camera_frame))

            for obj_detector_worker in self.object_detector_workers:
                obj_detection_response = obj_detector_worker.response_queue.get()
                present_objects[obj_detection_response.object_detector_name] = obj_detection_response.predictions

            logger.info("Finding present objects on all object detectors took {}".format(time.time() - t1))
            self.observer_thread.request_queue.task_done()
            if self.observer_thread.callback is not None:
                self.observer_thread.callback(present_objects)

    def get_present_objects(self, camera_frame, callback=None):
        if not self.observer_thread.request_queue.full():
            self.observer_thread.request_queue.put(camera_frame, block=False)
            self.observer_thread.callback = callback

    def stop(self):
        self.observer_thread.request_queue.put(POISON_PILL)
        self.observer_thread.join(timeout=2)
        self._stop_event.set()

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


class ObjectDetectionPrediction:
    def __init__(self, lable, confidence, top_left, bottom_right):
        self.lable = lable
        self.confidnece = confidence
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.image = None


class ObjectDetectionRequest:
    def __init__(self, camera_frame):
        self.camera_frame = camera_frame


class ObjectDetectionResponse:
    def __init__(self, obj_detector_name, predictions):
        self.object_detector_name = obj_detector_name
        self.predictions = predictions


class ObjectDetectorWorker(mp.Process):
    def __init__(self, object_detector, request_queue, response_queue):
        mp.Process.__init__(self)
        self.object_detector = object_detector
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.shut_down_event = mp.Event()

    def run(self):
        while True:
            if self.shut_down_event.is_set():
                logger.info("Shutting down: ", self.object_detector.name)
                self.request_queue.task_done()
                break

            obj_detection_request = self.request_queue.get()

            t1 = time.time()
            obj_detection_predictions = self.object_detector.get_predictions(obj_detection_request.camera_frame)
            self.request_queue.task_done()
            self.response_queue.put(ObjectDetectionResponse(self.object_detector.name, obj_detection_predictions))
            logger.info("Detection of objects by {} took {}".format(self.object_detector.name, time.time() - t1))

        return

    def shut_down(self):
        self.shut_down_event.set()