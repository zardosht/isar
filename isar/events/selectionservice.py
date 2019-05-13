import threading
import logging

from isar.scene.annotationmodel import Annotation

logger = logging.getLogger("isar.selectionservice")


class SelectionService:
    def __init__(self):
        self.annotations_model = None

    def on_event(self, selection_event):
        target = selection_event.target

        # # ------------ Experimental ------------
        # if isinstance(target, Annotation):
        #     if target.name == "lena":
        #         self.toggle_red_box()
        # # --------------------------------------

        on_select = getattr(target, "on_select", None)
        if on_select is not None and callable(on_select):

            t = threading.Thread(target=target.on_select)
            t.start()

    def stop(self):
        pass

    # # For testing
    # def toggle_red_box(self):
    #     if self.annotations_model is not None:
    #         red_box = self.annotations_model.get_annotation_by_name("red_box")
    #         if red_box is None:
    #             logger.warning("red_box is None")
    #         is_visible = red_box.show.get_value()
    #         red_box.show.set_value(not is_visible)


