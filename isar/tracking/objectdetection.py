import importlib
import logging
import os
import threading
import time
import traceback

from isar.services.service import Service

logger = logging.getLogger("isar.objectdetection")

"""
We consider each object detector as a plug-in.
For each object detector we start a worker process with the detector as an attribute.
Each worker process has a task and result queue. 
When the service starts we start all teh object detector worker processes and join them. 
When the service stops we terminate all the worker processes. 
"""

OBJECT_DETOCTORS_PATH = "./objectdetectors"

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


def init():
    """
    Search the object detectors plugin directory and populate the object_detectors and physical_objects dictionaries
    :return:
    """
    global object_detectors
    entries = os.listdir(OBJECT_DETOCTORS_PATH)
    for path_entry in entries:
        path = os.path.join(OBJECT_DETOCTORS_PATH, path_entry)
        if not os.path.isdir(path) or not OBJECT_DETECTOR_MODULE_FILENAME in os.listdir(path):
            continue
        try:
            module_path = os.path.join(path, OBJECT_DETECTOR_MODULE_FILENAME)
            spec = importlib.util.spec_from_file_location(OBJECT_DETECTOR_MODULE_NAME, module_path)
            obj_detector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(obj_detector)
            object_detectors[obj_detector.name] = obj_detector
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

    def start(self):
        """
        Start a process for each of the object detectors.
        :return:
        """
        pass

    def _start_detection(self):
        while not self._stop_event.is_set():
            time.sleep(5)
            logger.info("Object detection.")
            pass

    def stop(self):
        self._stop_event.set()

    def get_physical_objects(self):
        """
        :return: A dictionary with object detector name as key and the list of physical objects
        that this object detector can detect as value.
        """
        global physical_objects
        # TODO: read it from the description of the object detection models. Check if the init is finished and the
        #  dictionary is populated

        return physical_objects


class ObjectDetectionResult:
    def __init__(self, lable, confidence, top_left, bottom_right):
        self.lable = lable
        self.confidnece = confidence
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.image = None


class ObjectDetectionRequest:
    def __init__(self):
        self.camera_frame = None


class ObjectDetectionResponse:
    def __init__(self):
        self.object_detectors_name = None
        self.predictions = None