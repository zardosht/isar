import logging

from isar.events import eventmanager
from isar.events.events import HandOnTopEvent
from isar.scene.annotationmodel import ActionButtonAnnotation
from isar.tracking.selectionstick import SelectionStickService

logger = logging.getLogger("isar.handtracking")


class HandTrackingService(SelectionStickService):
    def __init__(self, service_name=None, camera_service=None):
        super().__init__(service_name, camera_service)
        self.MARKER_ID = 3
        self.trigger_interval = HandOnTopEvent.trigger_interval
        self.repeat_interval = HandOnTopEvent.repeat_interval

    def fire_event(self, target):
        logger.info("Fire HandOnTopEvent on: " + str(target))
        scene_id = self._annotations_model.get_current_scene().name

        if isinstance(target, ActionButtonAnnotation):
            eventmanager.fire_selection_event(target, scene_id)
        else:
            eventmanager.fire_hand_on_top_event(target, scene_id)
