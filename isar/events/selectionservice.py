import threading
import logging

from isar.events import eventmanager
from isar.events.events import SelectionEvent
from isar.scene.annotationmodel import Annotation, ActionButtonAnnotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.services.service import Service

logger = logging.getLogger("isar.selectionservice")


class SelectionService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.annotations_model = None
        self.actions_service = None

        eventmanager.register_listener(SelectionEvent.__name__, self)

    def on_event(self, selection_event):
        target = selection_event.target

        # ------------ Experimental ------------
        if isinstance(target, Annotation):
            if target.name == "lenna":
                toggle_red_box_action = self.actions_service.get_action_by_name("Toggle Red Box")
                self.actions_service.perform_action(toggle_red_box_action)

        if isinstance(target, PhysicalObject):
            if target.name == "Pincers":
                action = self.actions_service.get_action_by_name("Play Pincers Audio")
                self.actions_service.perform_action(action)

        # --------------------------------------

        on_select = getattr(target, "on_select", None)
        if on_select is not None and callable(on_select):
            t = threading.Thread(target=target.on_select)
            t.start()

        if isinstance(target, ActionButtonAnnotation):
            action = target.on_select_action.get_value()
            self.actions_service.perform_action(action)

    def stop(self):
        pass


