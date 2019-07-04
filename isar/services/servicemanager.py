import logging
import traceback
from enum import Enum

from isar.camera.camera import CameraService
from isar.events import eventmanager
from isar.events.actionsservice import ActionsService
from isar.events.checkboxservice import CheckboxService
from isar.events.events import SelectionEvent, TimerTickEvent, TimerFinishedEvent, TimerTimeout1Event
from isar.events.objecttrackingservice import ObjectTrackingService
from isar.events.rulesservice import RulesService
from isar.events.selectionservice import SelectionService
from isar.events.timerservice import TimerService
from isar.tracking import objectdetection
from isar.tracking.handtracking import HandTrackingService
from isar.tracking.objectdetection import ObjectDetectionService
from isar.tracking.selectionstick import SelectionStickService

__services = {}


logger = logging.getLogger("isar.service.servicemanager")


class ServiceNames(Enum):
    CAMERA1 = 1
    OBJECT_DETECTION = 2
    PROJECTOR = 3
    SELECTION_STICK = 4
    SELECTION_SERVICE = 5
    HAND_TRACKING_SERVICE = 6
    ACTIONS_SERVICE = 7
    TIMER_SERVICE = 8
    RULES_SERVICE = 9
    OBJECT_TRACKING_SERVICE = 10
    CHECKBOX_SERVICE = 11


def start_services():
    try:
        camera1_service = CameraService(ServiceNames.CAMERA1, 2)
        camera1_service.start()
        __services[ServiceNames.CAMERA1] = camera1_service
    except Exception as exp:
        logger.error("Could not initialize camera service. Return.")
        logger.error("Please check the camera is connected and working.")
        traceback.print_tb(exp.__traceback__)
        return False

    try:
        objectdetection.init()
        objectdetection_service = ObjectDetectionService(ServiceNames.OBJECT_DETECTION, camera1_service)
        objectdetection_service.start()
        __services[ServiceNames.OBJECT_DETECTION] = objectdetection_service
    except Exception as exp:
        logger.error(exp)
        traceback.print_tb(exp.__traceback__)
        return False

    try:
        actions_service = ActionsService(ServiceNames.ACTIONS_SERVICE)
        __services[ServiceNames.ACTIONS_SERVICE] = actions_service

        selection_stick_service = SelectionStickService(ServiceNames.SELECTION_STICK, camera1_service)
        selection_stick_service.start()
        __services[ServiceNames.SELECTION_STICK] = selection_stick_service

        selection_service = SelectionService(ServiceNames.SELECTION_SERVICE)
        selection_service.actions_service = actions_service
        __services[ServiceNames.SELECTION_SERVICE] = selection_service

        hand_tracking_service = HandTrackingService(ServiceNames.HAND_TRACKING_SERVICE, camera1_service)
        hand_tracking_service.start()
        __services[ServiceNames.HAND_TRACKING_SERVICE] = hand_tracking_service

        timer_service = TimerService(ServiceNames.TIMER_SERVICE)
        timer_service.actions_service = actions_service
        __services[ServiceNames.SELECTION_SERVICE] = timer_service

        rules_service = RulesService(ServiceNames.RULES_SERVICE)
        rules_service.actions_service = actions_service
        __services[ServiceNames.RULES_SERVICE] = rules_service

        object_tracking_service = ObjectTrackingService(ServiceNames.OBJECT_TRACKING_SERVICE)
        __services[ServiceNames.OBJECT_TRACKING_SERVICE] = object_tracking_service

        checkbox_service = CheckboxService(ServiceNames.CHECKBOX_SERVICE)
        __services[ServiceNames.CHECKBOX_SERVICE] = checkbox_service

    except Exception as exp:
        logger.error(exp)
        traceback.print_tb(exp.__traceback__)
        return False

    return True


def stop_services():
    for service in __services.values():
        try:
            service.stop()
        except Exception as exp:
            logger.error(exp)
            traceback.print_tb(exp.__traceback__)

    # camera service must stop last.
    # when it stops, it puts some None objects in its queue
    # if any thread is waiting for camera service queue, it can pick the None object and continue termination.
    camera_service = get_service(ServiceNames.CAMERA1)
    camera_service.stop()


def get_service(service_name):
    return __services[service_name]


def current_scene_changed(current_scene):
    for service in __services.values():
        if getattr(service, "set_current_scene", None) is not None:
            service.set_current_scene(current_scene)


def on_project_loaded():
    # Services can re-initialize for the new project
    for service in __services.values():
        if getattr(service, "on_project_loaded", None) is not None:
            service.on_project_loaded()
