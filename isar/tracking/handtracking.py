import logging

from isar.events import eventmanager
from isar.tracking.selectionstick import SelectionStickService

logger = logging.getLogger("isar.handtracking")


class HandTrackingService(SelectionStickService):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.MARKER_ID = 3

    def fire_event(self, target):
        logger.info("Fire HandOnTopEvent on: " + str(target))
        scene_id = self._annotations_model.get_current_scene().name
        eventmanager.fire_hand_on_top_event(target, scene_id)
