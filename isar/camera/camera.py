import logging
import threading
from queue import Queue
import cv2

from isar.services.service import Service

logger = logging.getLogger("isar.camera")


class CameraService(Service):
    """
    Starts the OpenCV capturing and puts the frame in order in the FIFO queue
    """

    def __init__(self, service_name=None, cam_id=0):
        super().__init__(service_name)
        _queue_size = 5
        self._queue = Queue(_queue_size)
        self.cam_id = cam_id
        self._capture = None
        self._open_capture()
        self._stop_event = threading.Event()
        self._do_capture = False

    def _open_capture(self):
        self._capture = cv2.VideoCapture(self.cam_id)
        if not self._capture.isOpened():
            raise Exception("Could not open camera {0}".format(self.cam_id))

    def start(self):
        t = threading.Thread(target=self._start_capture)
        t.start()

    def _start_capture(self):
        """
        Read OpenCV frames and put them in the Queue.
        It blocks if the queue is full.
        """
        if not self._capture.isOpened():
            self._open_capture()

        frame_number = -1
        while not self._stop_event.is_set():
            if not self._do_capture:
                continue

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

    def start_capture(self):
        self._do_capture = True

    def stop_capture(self):
        self._do_capture = False

    def get_frame(self, flipped=False):
        """
        Return the frame from FIFO queue
        It blocks if the queue is empty.
        :return:
        """
        camera_frame = self._queue.get()
        if flipped:
            camera_frame.image = cv2.flip(camera_frame.image, 1)

        return camera_frame

    def get_camera_capture_size(self):
        if self._capture:
            width = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
            height = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            return width, height
        else:
            return None


class CameraFrame:
    """
    An OpenCV image plus the frame number
    """
    def __init__(self, image, frame_number):
        self.image = image
        self.frame_number = frame_number

    @property
    def size(self):
        return self.image.shape[1], self.image.shape[0]

