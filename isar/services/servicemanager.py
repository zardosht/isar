import logging
import traceback
from enum import Enum

from isar.camera.camera import CameraService
from isar.events import eventmanager
from isar.events.actionsservice import ActionsService
from isar.events.eventmanager import SelectionEvent, TimerTickEvent, TimerFinishedEvent, TimerTimeout1Event
from isar.events.selectionservice import SelectionService
from isar.events.timerservice import TimerService
from isar.tracking.selectionstick import SelectionStickService

__services = {}


logger = logging.getLogger("isar.service.servicemanager")


class ServiceNames(Enum):
    CAMERA1 = 1
    OBJECT_DETECTION = 2
    PROJECTOR = 3
    SELECTION_STICK = 4
    SELECTION_SERVICE = 5
    ACTIONS_SERVICE = 6
    TIMER_SERVICE = 7


def start_services():
    try:
        camera1_service = CameraService(ServiceNames.CAMERA1, 0)
        camera1_service.start()
        __services[ServiceNames.CAMERA1] = camera1_service
    except Exception as exp:
        logger.error(exp)
        traceback.print_tb(exp.__traceback__)

    # try:
    #     objectdetection.init()
    #     objectdetection_service = ObjectDetectionService(ServiceNames.OBJECT_DETECTION)
    #     objectdetection_service.start()
    #     __services[ServiceNames.OBJECT_DETECTION] = objectdetection_service
    # except Exception as exp:
    #     logger.error(exp)
    #     traceback.print_tb(exp.__traceback__)

    try:
        actions_service = ActionsService(ServiceNames.ACTIONS_SERVICE)
        __services[ServiceNames.ACTIONS_SERVICE] = actions_service

        selection_stick_service = SelectionStickService(ServiceNames.SELECTION_STICK)
        selection_stick_service.start()
        __services[ServiceNames.SELECTION_STICK] = selection_stick_service

        selection_service = SelectionService(ServiceNames.SELECTION_SERVICE)
        selection_service.actions_service = actions_service
        eventmanager.register_listener(SelectionEvent.__name__, selection_service)
        __services[ServiceNames.SELECTION_SERVICE] = selection_service

        timer_service = TimerService(ServiceNames.TIMER_SERVICE)
        timer_service.actions_service = actions_service
        eventmanager.register_listener(TimerTickEvent.__name__, timer_service)
        eventmanager.register_listener(TimerFinishedEvent.__name__, timer_service)
        eventmanager.register_listener(TimerTimeout1Event.__name__, timer_service)
        eventmanager.register_listener(TimerTimeout1Event.__name__, timer_service)
        eventmanager.register_listener(TimerTimeout1Event.__name__, timer_service)
        __services[ServiceNames.SELECTION_SERVICE] = timer_service

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
