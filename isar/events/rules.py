import logging
import time

from isar.events.events import SceneShownEvent
from isar.services import servicemanager
from isar.services.servicemanager import ServiceNames


logger = logging.getLogger("isar.scene.rules")


class Rule:
    def __init__(self):
        self.name = None
        self.scene = None
        self.event = None
        self.action = None
        self._actionsservice = servicemanager.get_service(ServiceNames.ACTIONS_SERVICE)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_actionsservice"]
        return state

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)

    def fire(self):
        if self._actionsservice is None:
            logger.error("self.actionsservice is None. Return.")
            return

        if self._actionsservice.current_scene != self.scene:
            logger.error("self.actionsservice.current_scene not the same as self.scene. Return.")
            return

        if isinstance(self.event, SceneShownEvent):
            time.sleep(SceneShownEvent.delay)

        self._actionsservice.perform_action(self.action)
