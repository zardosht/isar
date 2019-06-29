import logging
import time

from isar.events import eventmanager
from isar.events.events import PhysicalObjectGroupAppearedEvent, HandOnTopEvent, PhysicalObjectPlacedInAreaEvent, \
    PhysicalObjectRemovedFromAreaEvent
from isar.scene.annotationmodel import ObjectAreaAnnotation
from isar.scene.physicalobjectmodel import PhysicalObjectsModel, PhysicalObject
from isar.services.service import Service

logger = logging.getLogger("isar.objecttrackingservice")


"""
Keeps track of which objects are on the table, and fires PhysicalObjectAppeared, PhysicalObjectDisappeared, 
PhysicalObjectPicked, and PhysicalObjectGroupAppeared events. 
"""

# These are added to counter the flickering effect of firing appear, disappear events, when tracking is not robust.
MIN_INTERVAL_BETWEEN_FIRING_APPEAR_EVENTS = 1
MIN_INTERVAL_BETWEEN_FIRING_DISAPPEAR_EVENTS = 1


class ObjectTrackingService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)

        self.__annotations_model = None
        self.__scenes_model = None
        self.__physical_objects_model = None

        self.current_scene = None

        self.object_group_appeared_events = []
        self.object_appeared_dict = {}
        self.object_disappeared_dict = {}

        eventmanager.register_listener(HandOnTopEvent.__name__, self)
        self.hand_on_top_phys_obj = None

        self.object_area_annotations = []
        self.object_areas_dict = {}
        self.obj_placed_in_area_events = []
        self.obj_removed_from_area_events = []

    def on_event(self, hand_on_top_event):
        self.hand_on_top_phys_obj = None
        target = hand_on_top_event.target
        if isinstance(target, PhysicalObject):
            self.hand_on_top_phys_obj = target

    def set_annotations_model(self, annotations_model):
        self.__annotations_model = annotations_model

    def set_scenes_model(self, scenes_model):
        self.__scenes_model = scenes_model

    def set_physical_objects_model(self, phys_objs_model):
        self.__physical_objects_model = phys_objs_model
        self.__physical_objects_model.tracking_lost.connect(self.tracking_lost)
        self.__physical_objects_model.tracking_captured.connect(self.tracking_captured)

    def set_current_scene(self, current_scene):
        self.current_scene = current_scene
        self.object_group_appeared_events = self.current_scene.get_events_by_type(PhysicalObjectGroupAppearedEvent)
        self.object_appeared_dict.clear()
        self.object_disappeared_dict.clear()

        self.object_areas_dict.clear()
        self.object_area_annotations = self.current_scene.get_all_annotations_by_type(ObjectAreaAnnotation)
        for obj_area_annotation in self.object_area_annotations:
            self.object_areas_dict[obj_area_annotation] = []

        self.obj_placed_in_area_events = self.current_scene.get_events_by_type(PhysicalObjectPlacedInAreaEvent)
        self.obj_removed_from_area_events = self.current_scene.get_events_by_type(PhysicalObjectRemovedFromAreaEvent)

    def tracking_lost(self, phys_obj):
        logger.info("Tracking lost: {}".format(phys_obj.name))
        if phys_obj not in self.object_disappeared_dict:
            self.object_disappeared_dict[phys_obj] = time.time()
            if phys_obj in self.object_appeared_dict:
                del self.object_appeared_dict[phys_obj]

            eventmanager.fire_physical_object_disappeared_event(phys_obj, self.current_scene.name)
            if phys_obj == self.hand_on_top_phys_obj:
                eventmanager.fire_physical_object_picked_event(phys_obj, self.current_scene.name)
        else:
            last_disappear_event_fired_at = self.object_disappeared_dict[phys_obj]
            delta = time.time() - last_disappear_event_fired_at
            if delta > MIN_INTERVAL_BETWEEN_FIRING_DISAPPEAR_EVENTS:
                self.object_disappeared_dict[phys_obj] = time.time()
                if phys_obj in self.object_appeared_dict:
                    del self.object_appeared_dict[phys_obj]
                eventmanager.fire_physical_object_disappeared_event(phys_obj, self.current_scene.name)
                if phys_obj == self.hand_on_top_phys_obj:
                    eventmanager.fire_physical_object_picked_event(phys_obj, self.current_scene.name)

        self.update_object_areas_dict(phys_obj, object_appeared=False)

    def tracking_captured(self, phys_obj):
        logger.info("Tracking captured: {}".format(phys_obj.name))
        if phys_obj not in self.object_appeared_dict:
            self.object_appeared_dict[phys_obj] = time.time()
            eventmanager.fire_physical_object_appeared_event(phys_obj, self.current_scene.name)

        else:
            last_appear_event_fired_at = self.object_appeared_dict[phys_obj]
            delta = time.time() - last_appear_event_fired_at
            if delta > MIN_INTERVAL_BETWEEN_FIRING_APPEAR_EVENTS:
                self.object_appeared_dict[phys_obj] = time.time()
                eventmanager.fire_physical_object_appeared_event(phys_obj, self.current_scene.name)

        for obj_group_appeared_event in self.object_group_appeared_events:
            self.check_and_fire_obj_group_appeared_event(obj_group_appeared_event)

        self.update_object_areas_dict(phys_obj, object_appeared = True)

    def check_and_fire_obj_group_appeared_event(self, obj_group_appeared_event):
        targets = obj_group_appeared_event.targets
        targets_present = [False] * len(targets)
        for i in range(len(targets)):
            if targets[i].name in self.object_appeared_dict:
                targets_present[i] = True

        if len(targets_present) > 0 and all(targets_present):
            eventmanager.fire_physical_object_group_appeared_event(obj_group_appeared_event)

    def update_object_areas_dict(self, phys_obj, object_appeared):
        if object_appeared:
            center = phys_obj.get_center()
            for obj_area_annotation in self.object_area_annotations:
                if obj_area_annotation.intersects_with_point(center):
                    # object in the area
                    if phys_obj not in self.object_areas_dict[obj_area_annotation]:
                        self.object_areas_dict[obj_area_annotation].append(phys_obj)

                        for obj_placed_in_area_event in self.obj_placed_in_area_events:
                            if obj_placed_in_area_event.target == obj_area_annotation \
                                    and obj_placed_in_area_event.physical_object == phys_obj:
                                eventmanager.fire_object_placed_in_area_event(obj_placed_in_area_event)
                else:
                    if phys_obj in self.object_areas_dict[obj_area_annotation]:
                        self.object_areas_dict[obj_area_annotation].remove(phys_obj)

                        for obj_removed_from_area_event in self.obj_removed_from_area_events:
                            if obj_removed_from_area_event.target == obj_area_annotation \
                                    and obj_removed_from_area_event.physical_object == phys_obj:
                                eventmanager.fire_object_remove_from_area_event(obj_removed_from_area_event)

        else:
            for obj_area_annotation in self.object_area_annotations:
                if phys_obj in self.object_areas_dict[obj_area_annotation]:
                    self.object_areas_dict[obj_area_annotation].remove(phys_obj)

                    for obj_removed_from_area_event in self.obj_removed_from_area_events:
                        if obj_removed_from_area_event.target == obj_area_annotation \
                                and obj_removed_from_area_event.physical_object == phys_obj:
                            eventmanager.fire_object_remove_from_area_event(obj_removed_from_area_event)

    def stop(self):
        pass
