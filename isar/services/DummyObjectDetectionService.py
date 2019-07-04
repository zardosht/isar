from isar.services.service import Service
from isar.tracking import objectdetection


class DummyObjectDetectionService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)

    @staticmethod
    def get_physical_objects():
        return objectdetection.physical_objects

    def stop_object_detection(self):
        pass
