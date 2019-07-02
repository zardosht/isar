import logging
from threading import Thread

from isar.events import events, eventmanager
from isar.services.service import Service

logger = logging.getLogger("isar.scene.rulesservice")


class RulesService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.actions_service = None
        self.__scenes_model = None
        self.current_scene = None

        self.register_for_all_events()

    def register_for_all_events(self):
        for event_class_name in events.event_types:
            eventmanager.register_listener(event_class_name, self)

    def set_scenes_model(self, scenes_model):
        self.__scenes_model = scenes_model

    def set_current_scene(self, current_scene):
        self.current_scene = current_scene

    def on_event(self, event):
        if self.current_scene is None:
            logger.error("self.scene is None. Return.")
            return

        for rule in self.current_scene.get_rules():
            if rule.event == event:
                t = Thread(name="RuleServiceFireRuleThread", target=rule.fire)
                t.start()
