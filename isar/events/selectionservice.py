import threading
import logging

from isar.events import actionsservice
from isar.scene.annotationmodel import Annotation, ActionButtonAnnotation
from isar.services.service import Service

logger = logging.getLogger("isar.selectionservice")


class SelectionService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.annotations_model = None
        self.actions_service = None

    def on_event(self, selection_event):
        target = selection_event.target

        # ------------ Experimental ------------
        if isinstance(target, Annotation):
            if target.name == "lenna":
                toggle_red_box_action = actionsservice.defined_actions[0]
                self.actions_service.perform_action(toggle_red_box_action)
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


