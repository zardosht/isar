from isar.services.service import Service


class DummyObjectSelectionStickService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)

    def stop_object_detection(self):
        pass
