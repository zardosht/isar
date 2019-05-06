import logging
import traceback
from enum import Enum

from isar.camera.camera import CameraService
from isar.events import eventmanager
from isar.events.eventmanager import SelectionEvent
from isar.events.selectionservice import SelectionService
from isar.tracking import objectdetection
from isar.tracking.objectdetection import ObjectDetectionService
from isar.tracking.selectionstick import SelectionStickService

__services = {}


logger = logging.getLogger("isar.service.servicemanager")


class ServiceNames(Enum):
    CAMERA1 = 1
    OBJECT_DETECTION = 2
    PROJECTOR = 3
    SELECTION_STICK = 4


def start_services():
    try:
        camera1_service = CameraService(ServiceNames.CAMERA1, 2)
        camera1_service.start()
        __services[ServiceNames.CAMERA1] = camera1_service
    except Exception as exp:
        logger.error(exp)
        traceback.print_tb(exp.__traceback__)

    try:
        objectdetection.init()
        objectdetection_service = ObjectDetectionService(ServiceNames.OBJECT_DETECTION)
        objectdetection_service.start()
        __services[ServiceNames.OBJECT_DETECTION] = objectdetection_service
    except Exception as exp:
        logger.error(exp)
        traceback.print_tb(exp.__traceback__)

    try:
        selection_stick_service = SelectionStickService(ServiceNames.SELECTION_STICK)
        selection_stick_service.start()
        __services[ServiceNames.SELECTION_STICK] = selection_stick_service

        selection_service = SelectionService()
        eventmanager.register_listener(SelectionEvent.__name__, selection_service)
    except Exception as exp:
        logger.error(exp)
        traceback.print_tb(exp.__traceback__)


def stop_services():
    for service in __services.values():
        try:
            service.stop()
        except Exception as exp:
            logger.error(exp)
            traceback.print_tb(exp.__traceback__)


def get_service(service_name):
    return __services[service_name]
