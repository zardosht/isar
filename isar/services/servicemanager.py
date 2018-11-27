from enum import Enum

from isar.camera.camera import CameraService


_services = {}


class ServiceNames(Enum):
    CAMERA1 = 1


def start_services():
    camera1_service = CameraService(ServiceNames.CAMERA1, 0)
    camera1_service.start()
    _services[ServiceNames.CAMERA1] = camera1_service


def stop_services():
    for service in _services.values():
        service.stop()


def get_service(service_name):
    return _services[service_name]
