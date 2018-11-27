import logging
import threading
from queue import Queue
import cv2

logger = logging.getLogger("isar.camera")


class CameraService(threading.Thread):
    """
    Starts the OpenCV capturing and puts the frame in order in the FIFO queue
    """
    def __init__(self, cam_id=0):
        super().__init__()
        _queue_size = 5
        self._queue = Queue(_queue_size)
        self.cam_id = cam_id
        self._capture = None
        self._open_capture()
        self._stop_event = threading.Event()

    def _open_capture(self):
        self._capture = cv2.VideoCapture(self.cam_id)
        if not self._capture.isOpened():
            raise Exception("Could not open camera {0}".format(self.cam_id))

    def run(self):
        """
        Read OpenCV frames and put them in the Queue.
        It blocks if the queue is full.
        """
        if not self._capture.isOpened():
            self._open_capture()

        frame_number = -1
        while not self._stop_event.is_set():
            if self._queue.full():
                continue

            ret, frame = self._capture.read()
            if ret:
                frame_number += 1
                camera_frame = CameraFrame(frame, frame_number)
                self._queue.put(camera_frame)
            else:
                logger.error("Capture was unsuccessful.")

    def stop(self):
        """
        Stop capturing
        :return:
        """
        self._stop_event.set()
        self._capture.release()

    def get_frame(self):
        """
        Return the frame from FIFO queue
        It blocks if the queue is empty.
        :return:
        """
        return self._queue.get()


class CameraFrame:
    """
    An OpenCV image plus the frame number
    """
    def __init__(self, image, frame_number):
        self.image = image
        self.frame_number = frame_number

