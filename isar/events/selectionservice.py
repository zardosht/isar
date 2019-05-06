import threading
import logging


logger = logging.getLogger("isar.selectionservice")


class SelectionService:
    @staticmethod
    def on_event(selection_event):
        target = selection_event.target
        on_select = getattr(target, "on_select", None)
        if on_select is not None and callable(on_select):
            t = threading.Thread(target=target.on_select)
            t.start()


