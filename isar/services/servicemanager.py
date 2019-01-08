from enum import Enum

from isar.camera.camera import CameraService
from isar.tracking import objectdetection
from isar.tracking.objectdetection import ObjectDetectionService

__services = {}


class ServiceNames(Enum):
    CAMERA1 = 1
    OBJECT_DETECTION = 2


def start_services():
    camera1_service = CameraService(ServiceNames.CAMERA1, 2)
    camera1_service.start()
    __services[ServiceNames.CAMERA1] = camera1_service

    objectdetection.init()
    objectdetection_service = ObjectDetectionService(ServiceNames.OBJECT_DETECTION)
    objectdetection_service.start()
    __services[ServiceNames.OBJECT_DETECTION] = objectdetection_service


def stop_services():
    for service in __services.values():
        service.stop()


def get_service(service_name):
    return __services[service_name]
