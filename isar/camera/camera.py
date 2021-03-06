import logging
import platform
import threading
from queue import LifoQueue
import cv2

import isar
from isar.services.service import Service

logger = logging.getLogger("isar.camera")


class CameraService(Service):
    """
    Starts the OpenCV capturing and puts the frame in order in the FIFO queue
    """

    def __init__(self, service_name=None, cam_id=0):
        super().__init__(service_name)

        _queue_size = 20
        self._queue = LifoQueue(_queue_size)

        # self._queue_size = 20
        # self._queue = Queue(self._queue_size)

        self.cam_id = cam_id
        self._capture = None
        self._open_capture()
        self._stop_event = threading.Event()
        self._do_capture = False

    def _open_capture(self):
        if isar.PLATFORM == "Windows":
            self._capture = cv2.VideoCapture(self.cam_id, cv2.CAP_DSHOW)
            width = 1920
            height = 1080
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        elif isar.PLATFORM == "Linux":
            self._capture = cv2.VideoCapture(self.cam_id, cv2.CAP_V4L2)
            self._capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            width = 1920
            height = 1080
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        else:  # Darwin
            self._capture = cv2.VideoCapture(self.cam_id)

            # TODO: possibly for later
            # width = 1920
            # height = 1080
            # self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            # self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            # self.capture.set(cv2.CAP_PROP_FPS, 24)

        if not self._capture.isOpened():
            message = "Could not open camera {}".format(self.cam_id)
            raise Exception(message)

    def start(self):
        t = threading.Thread(name="CameraThread", target=self._start_capture)
        t.daemon = True
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
                # logger.warning("Camera _queue is full! continue.")
                continue

            # time.sleep(0.05)

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

        for i in range(100):
            try:
                self._queue.get_nowait()
            except:
                pass

        for i in range(100):
            try:
                self._queue.put_nowait(isar.POISON_PILL)
            except:
                pass

        # TODO: this hangs on stop! why? I don't know
        # self._capture.release()

    def release_capture(self):
        self._capture.release()

    def start_capture(self):
        self._do_capture = True

    def stop_capture(self):
        self._do_capture = False

    def get_frame(self, flipped_x=False, flipped_y=False):
        """
        Return the frame from FIFO queue
        It blocks if the queue is empty.
        :return:
        """
        if not self._do_capture:
            raise RuntimeError("_do_capture is False. Have you forgotten to call start_capture() first?")

        if self._queue.empty():
            # logger.warning("Camera _queue is empty! Return None.")
            return None

        camera_frame = self._queue.get()
        if flipped_x:
            camera_frame.flip(0)

        if flipped_y:
            camera_frame.flip(1)

        return camera_frame

    def get_camera_capture_size(self):
        if self._capture:
            width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))  # float
            height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        else:
            return None


class CameraFrame:
    """
    An OpenCV image plus the frame number
    """
    def __init__(self, image, frame_number):
        self.raw_image = image
        self.scene_image = image.copy()
        self.frame_number = frame_number

    def flip(self, flip_code):
        # flipCode	a flag to specify how to flip the array;
        # 0 means flipping around the x-axis and
        # positive value (for example, 1) means flipping around y-axis.
        # Negative value (for example, -1) means flipping around both axes.
        self.raw_image = cv2.flip(self.raw_image, flip_code)
        self.scene_image = cv2.flip(self.scene_image, flip_code)

    @property
    def size(self):
        return self.raw_image.shape[1], self.raw_image.shape[0]

