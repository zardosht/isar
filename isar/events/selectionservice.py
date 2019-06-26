import threading
import logging

from isar.events import eventmanager
from isar.events.events import SelectionEvent
from isar.scene.annotationmodel import ActionButtonAnnotation
from isar.services.service import Service


logger = logging.getLogger("isar.selectionservice")


class SelectionService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.annotations_model = None
        self.actions_service = None
        self.current_scene = None

        eventmanager.register_listener(SelectionEvent.__name__, self)

    def on_event(self, selection_event):
        target = selection_event.target
        logger.info("SelectionEvent on {}".format(str(target)))

        on_select = getattr(target, "on_select", None)
        if on_select is not None and callable(on_select):
            t = threading.Thread(target=target.on_select)
            t.start()

        if isinstance(target, ActionButtonAnnotation):
            action = target.on_select_action.get_value()
            self.actions_service.perform_action(action)

    def set_current_scene(self, current_scene):
        self.current_scene = current_scene

    def stop(self):
        pass
