import logging
import threading
import time

from isar.services.service import Service

logger = logging.getLogger("isar.objectdetection")


class ObjectDetectionService(Service):
    def __init__(self, service_name=None):
        super().__init__(service_name)
        self._stop_event = threading.Event()

    def start(self):
        t = threading.Thread(target=self._start_detection)
        t.start()

    def _start_detection(self):
        while not self._stop_event.is_set():
            time.sleep(5)
            logger.info("Object detection.")
            pass

    def stop(self):
        self._stop_event.set()

