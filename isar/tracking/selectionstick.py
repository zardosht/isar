import cv2
import threading

from isar.scene import sceneutil
from isar.services.service import Service


'''
— a thread for detecting the marker
This thread continoisly detects the marker, and updates self.current_rect

— a thread for firing selection events: 
This thread continoisly queries scene physical objects and annotations for colliding with the center 
point of self.current_rect. If a collision is detected, the timestamp is recorded. 
If after 3 seconds the collision is still active, a SelectionEvent is fired, 
with list of annotations and physical objects that are selected. 

— An event manager that registers listeners for different event types and fires the events. 
Firing an event means calling all listeners for that event with the given event params. 

— A selection service that is listener for SelectionEvents. 
When event is called, the on_select() event of all parameter 
annotations and physical objects is called (in a separate thread?)

'''


class SelectionStickService(Service):
    def __init__(self, service_name=None):
        super().__init__(service_name)
        self._stop_event = threading.Event()
        self.camera_img = None
        self.__current_rect = None

    def start(self):
        tracking_thread = threading.Thread(target=self._start_tracking)
        tracking_thread.start()

        event_detection_thread = threading.Thread(target=self._start_event_detection)
        event_detection_thread.start()

    def _start_tracking(self):
        while not self._stop_event.is_set():
            if self.camera_img is not None:
                marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(self.camera_img, sceneutil.aruco_dictionary)
                if marker_ids is None:
                    self.__current_rect = None
                    continue

                index = -1
                for i, marker_id in enumerate(marker_ids):
                    if marker_id == 5:
                        index = i

                if index != -1:
                    self.__current_rect = marker_corners[index].reshape(4, 2)
                else:
                    self.__current_rect = None

    def _start_event_detection(self):
        while not self._stop_event.is_set():
            # get the center of marker rect
            # check if the center collides with any annotation and physcical objects.
            # put colliding objects/annotations with the timestamp in a dic
            # check the colliding objects, if more that three seconds colliding, then fire event.

            pass

    def stop(self):
        self._stop_event.set()

    def draw_current_rect(self, img):
        rect = self.__current_rect
        if rect is not None:
            rect_in_scene = sceneutil.camera_coords_to_scene_coord(rect)
            v1 = (int(rect_in_scene[0][0]), int(rect_in_scene[0][1]))
            v2 = (int(rect_in_scene[2][0]), int(rect_in_scene[2][1]))
            cv2.rectangle(img, v1, v2, (255, 0, 255), thickness=2)

    def get_current_rect(self):
        return self.__current_rect



