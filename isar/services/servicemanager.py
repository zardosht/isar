from isar.camera.camera import CameraService

services = {}


def start_services():
    camera_service = CameraService()
    camera_service.start()
    services[CameraService.service_name] = camera_service


def stop_services():
    for service in services.values():
        service.stop()



