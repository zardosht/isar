import logging

from isar.events import eventmanager
from isar.events.events import CheckboxGroupCheckedEvent, CheckboxCheckedEvent, CheckboxUncheckedEvent
from isar.scene.annotationmodel import CheckboxAnnotation
from isar.services.service import Service

logger = logging.getLogger("isar.checkboxservice")


"""
Keeps track of checkbox annotations and fires ChckboxGroupChecked events. 
"""


class CheckboxService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)

        self.__annotations_model = None
        self.__scenes_model = None
        self.current_scene = None
        eventmanager.register_listener(CheckboxCheckedEvent.__name__, self)
        eventmanager.register_listener(CheckboxUncheckedEvent.__name__, self)

        self.checkbox_group_checked_events = []
        self.checked_checkboxes = set()

    def set_annotations_model(self, annotations_model):
        self.__annotations_model = annotations_model

    def set_scenes_model(self, scenes_model):
        self.__scenes_model = scenes_model

    def set_current_scene(self, current_scene):
        self.current_scene = current_scene
        self.checkbox_group_checked_events = self.current_scene.get_events_by_type(CheckboxGroupCheckedEvent)
        self.checked_checkboxes.clear()
        if self.__annotations_model is not None:
            checkboxes = self.__annotations_model.get_all_annotations_by_type(CheckboxAnnotation)
            for checkbox in checkboxes:
                if checkbox.checked.get_value():
                    self.checked_checkboxes.add(checkbox)

    def on_event(self, checkbox_event):
        checkbox = checkbox_event.target
        if isinstance(checkbox_event, CheckboxCheckedEvent):
            self.checked_checkboxes.add(checkbox)
            for checkbox_group_checked_event in self.checkbox_group_checked_events:
                self.check_and_fire_checkbox_group_checked_event(checkbox_group_checked_event)

        elif isinstance(checkbox_event, CheckboxUncheckedEvent):
            if checkbox in self.checked_checkboxes:
                self.checked_checkboxes.remove(checkbox)

    def check_and_fire_checkbox_group_checked_event(self, checkbox_group_checked_event):
        targets = checkbox_group_checked_event.targets
        if set(targets).issubset(self.checked_checkboxes):
            logger.info("Checkbox Group checked.")
            eventmanager.fire_checkbox_group_checked_event(checkbox_group_checked_event)

    def stop(self):
        pass
