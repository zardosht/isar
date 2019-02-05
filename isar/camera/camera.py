import logging
import multiprocessing
import threading
import traceback
from ctypes import c_bool
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
        self._queue = multiprocessing.Queue(_queue_size)
        self.cam_id = cam_id
        self._capture = None

        # self._open_capture()

        self._do_capture = multiprocessing.Value(c_bool, False)
        self._stop_event = multiprocessing.Event()
        self._capture_process = None

    def start(self):
        # self._capture_process = multiprocessing.Process(target=self._start_capture, args=(self._capture, ))

        self._capture_process = CameraCaptureProcess(self.cam_id, self._queue, self._do_capture, self._stop_event)

        self._capture_process.daemon = True

        self._capture_process.start()

    def stop(self):
        """
        Stop capturing
        :return:
        """
        self.stop_capture()
        self._stop_event.set()
        self._capture_process.terminate()
        self._capture_process.join()

    def start_capture(self):
        self._do_capture.value = True

    def stop_capture(self):
        self._do_capture.value = False

    def get_frame(self, flipped=False):
        """
        Return the frame from FIFO queue
        It blocks if the queue is empty.
        :return:
        """
        camera_frame = None
        if not self._queue.empty():
            camera_frame = self._queue.get()
            if flipped:
                camera_frame.flip()

        return camera_frame

    def get_camera_capture_size(self):
        return self.capture_process.get_camera_capture_size()


class CameraCaptureProcess(multiprocessing.Process):
    def __init__(self, cam_id, cam_queue, do_capture, stop_event):
        super().__init__()
        self._capture = None
        self.cam_id = cam_id
        self._queue = cam_queue
        self.do_capture = do_capture
        self._stop_event = stop_event

    def _open_capture(self):
        try:
            self._capture = cv2.VideoCapture(self.cam_id)
        except Exception as exp:
            traceback.print_tb(exp.__traceback__)

        if not self._capture.isOpened():
            raise Exception("Could not open camera {}".format(self.cam_id))

    def run(self):
        """
        Read OpenCV frames and put them in the Queue.
        It blocks if the queue is full.
        """
        self._open_capture()
        frame_number = -1
        while not self._stop_event.is_set():
            if not self._capture or not self._capture.isOpened():
                logger.error("Capture is none or not open.")
                break

            if not self._do_capture.value:
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

    def get_camera_capture_size(self):
        if self._capture:
            width = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
            height = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            return width, height
        else:
            return None

    def terminate(self):
        self._capture.release()
        super().terminate()


class CameraFrame:
    """
    An OpenCV image plus the frame number
    """
    def __init__(self, image, frame_number):
        self.raw_image = image
        self.scene_image = image.copy()
        self.frame_number = frame_number

    def flip(self):
        self.raw_image = cv2.flip(self.raw_image, 1)
        self.scene_image = cv2.flip(self.scene_image, 1)

    @property
    def size(self):
        return self.raw_image.shape[1], self.raw_image.shape[0]

