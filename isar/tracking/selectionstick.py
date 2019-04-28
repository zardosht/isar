import cv2
import threading

from isar.scene import sceneutil
from isar.services.service import Service


class SelectionStickService(Service):
    def __init__(self, service_name=None):
        super().__init__(service_name)
        self._stop_event = threading.Event()
        self.camera_img = None
        self.current_rect = None

    def start(self):
        t = threading.Thread(target=self._start_detection)
        t.start()

    def _start_detection(self):
        while not self._stop_event.is_set():
            if self.camera_img is not None:
                marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(self.camera_img, sceneutil.aruco_dictionary)
                if marker_ids is None:
                    continue

                index = -1
                for i, marker_id in enumerate(marker_ids):
                    if marker_id == 5:
                        index = i

                if index != -1:
                    self.current_rect = marker_corners[index].reshape(4, 2)

    def stop(self):
        self._stop_event.set()

    def get_current_rect(self):
        return self.current_rect

