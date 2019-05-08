import logging
import time

import cv2
import threading

import numpy as np

from isar.events import eventmanager
from isar.events.eventmanager import SelectionEvent
from isar.scene import sceneutil
from isar.services.service import Service


"""
— a thread for detecting the marker
This thread continoisly detects the marker, and updates self.current_rect

— a thread for firing selection events: 
This thread continoisly queries scene physical objects and annotations for colliding with the center 
point of self.current_rect. If a collision is detected, the timestamp is recorded. 
If after "SelectionEvent.trigger_interval" seconds the collision is still active, a SelectionEvent is fired, 
with list of annotations and physical objects that are selected. 

— An event manager that registers listeners for different event types and fires the events. 
Firing an event means calling all listeners for that event with the given event params. 

— A selection service that is listener for SelectionEvents. 
When event is called, the on_select() event of all parameter 
annotations and physical objects is called (in a separate thread?)

"""


logger = logging.getLogger("isar.selectionstick")


class SelectionStickService(Service):
    def __init__(self, service_name=None):
        super().__init__(service_name)
        self._stop_event = threading.Event()
        self.camera_img = None
        self.__current_rect = None
        self.__physical_objects_model = None
        self.__annotations_model = None

        self.drawing_color = (255, 0, 255)
        self.object_name = None
        self.annotation_name = None
        self.annotation_position = ()

        self.event_timers_phys_obj = {}
        self.event_timers_annotation = {}

    def start(self):
        tracking_thread = threading.Thread(target=self._start_tracking)
        tracking_thread.start()

        event_detection_thread = threading.Thread(target=self._start_event_detection)
        event_detection_thread.start()

    def _start_tracking(self):
        while not self._stop_event.is_set():
            if self.camera_img is None:
                continue

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
        # get the center of marker rect
        # check if the center collides with any annotation and physcical objects.
        # put colliding objects/annotations with the timestamp in a dic
        # check the colliding objects, if more that three seconds colliding, then fire event.

        while not self._stop_event.is_set():
            if self.__current_rect is None:
                continue

            center_point = self.get_center_point(in_image_coordinates=True)
            if center_point is None:
                continue

            center_in_scene = sceneutil.camera_coord_to_scene_coord(center_point)

            collides_with_object = False
            for phys_obj in self.__physical_objects_model.get_scene_physical_objects():
                if phys_obj.collides_with_point(center_in_scene, sceneutil.scene_scale_factor_c):
                    phys_obj_name = phys_obj.name
                    collides_with_object = True
                    self.drawing_color = (0, 0, 255)
                    self.object_name = phys_obj_name

                    if phys_obj_name not in self.event_timers_phys_obj:
                        self.event_timers_phys_obj[phys_obj_name] = time.time()
                    else:
                        first = self.event_timers_phys_obj[phys_obj_name]
                        if time.time() - first > SelectionEvent.trigger_interval:
                            self.fire_selection_event(phys_obj)
                            del self.event_timers_phys_obj[phys_obj_name]

                    break

            if not collides_with_object:
                self.event_timers_phys_obj.clear()

            collides_with_annotation = False
            for annotation in self.__annotations_model.get_all_annotations():
                if annotation.intersects_with_point(center_in_scene):
                    collides_with_annotation = True
                    self.drawing_color = (0, 0, 255)
                    annotation_name = annotation.name
                    self.annotation_name = annotation_name
                    self.annotation_position = annotation.position.get_value()
                    if annotation.name not in self.event_timers_annotation:
                        self.event_timers_annotation[annotation_name] = time.time()
                    else:
                        first = self.event_timers_annotation[annotation_name]
                        if time.time() - first > SelectionEvent.trigger_interval:
                            self.fire_selection_event(annotation)
                            del self.event_timers_annotation[annotation_name]

            if not collides_with_annotation:
                self.event_timers_annotation.clear()

            if not collides_with_object and not collides_with_annotation:
                self.drawing_color = (255, 0, 255)
                self.object_name = None
                self.annotation_name = None
                self.event_timers_phys_obj.clear()
                self.event_timers_annotation.clear()

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def fire_selection_event(target):
        logger.info("Fire SelectionEvent on: " + str(target))
        selection_event = SelectionEvent(target)
        eventmanager.fire_event(selection_event)

    def draw_current_rect(self, img, camera_projector_homography=None, scene_homography=None):
        current_rect = self.__current_rect
        if current_rect is not None:
            if camera_projector_homography is not None:
                projected_points = cv2.perspectiveTransform(np.array([[current_rect[0], current_rect[2]]]), camera_projector_homography).squeeze()
                v1 = projected_points[0]
                v2 = projected_points[1]
            else:
                rect_in_scene = sceneutil.camera_coords_to_scene_coords(current_rect)
                v1 = (rect_in_scene[0][0], rect_in_scene[0][1])
                v2 = (rect_in_scene[2][0], rect_in_scene[2][1])

            v1 = (int(v1[0]), int(v1[1]))
            v2 = (int(v2[0]), int(v2[1]))

            cv2.rectangle(img, v1, v2, self.drawing_color, thickness=2)

            camera_coord = current_rect[1]
            scene_c_coord = sceneutil.camera_coord_to_scene_coord_c(camera_coord)
            projector_coord = v1
            scene_p_coord = sceneutil.projector_coord_to_scene_coord_p(projector_coord)
            persisted_coord = ()
            if self.annotation_name is not None:
                persisted_coord = self.annotation_position

            cv2.putText(img, "C: " + str(camera_coord), (v2[0], v2[1]), cv2.FONT_HERSHEY_COMPLEX, .5, self.drawing_color, 1)
            cv2.putText(img, "per: " + str(persisted_coord), (v2[0], v2[1] + 15), cv2.FONT_HERSHEY_COMPLEX, .5, self.drawing_color, 1)
            cv2.putText(img, "SC_C: " + str(scene_c_coord), (v2[0], v2[1] + 30), cv2.FONT_HERSHEY_COMPLEX, .5, self.drawing_color, 1)
            cv2.putText(img, "P: " + str(projector_coord), (v2[0], v2[1] + 45), cv2.FONT_HERSHEY_COMPLEX, .5, self.drawing_color, 1)
            cv2.putText(img, "SC_P: " + str(scene_p_coord), (v2[0], v2[1] + 60), cv2.FONT_HERSHEY_COMPLEX, .5, self.drawing_color, 1)

            if self.object_name is not None:
                cv2.putText(img, self.object_name, (v1[0], v1[1] - 10), cv2.FONT_HERSHEY_COMPLEX, .5, self.drawing_color, 1)

            if self.annotation_name is not None:
                cv2.putText(img, self.annotation_name, (v1[0], v1[1] - 10), cv2.FONT_HERSHEY_COMPLEX, .5, self.drawing_color, 1)

    def get_current_rect(self):
        return self.__current_rect

    def get_center_point(self, in_image_coordinates=True):
        rect = self.__current_rect
        if rect is None:
            return None

        v1 = rect[0]
        v2 = rect[2]

        center = (int((v1[0] + v2[0]) / 2), int((v1[1] + v2[1]) / 2))
        if in_image_coordinates:
            return center
        else:
            return sceneutil.camera_coord_to_scene_coord(center)

    def set_physical_objects_model(self, phm):
        self.__physical_objects_model = phm

    def set_annotations_model(self, phm):
        self.__annotations_model = phm






