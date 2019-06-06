import logging

from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames


logger = logging.getLogger("isar.scene.rules")


class Rule:
    def __init__(self):
        self.scene = None
        self.event = None
        self.action = None
        self.actionsservice = servicemanager.get_service(ServiceNames.ACTIONS_SERVICE)

    def fire(self):
        if self.actionsservice is None:
            logger.error("self.actionsservice is None. Return.")
            return

        if self.actionsservice.current_scene != self.scene:
            logger.error("self.actionsservice.current_scene not the same as self.action. Return.")
            return

        self.actionsservice.perform_action(self.action)

