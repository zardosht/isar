from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from isar.events.events import SelectionEvent
from isar.scene.annotationmodel import Annotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene


class SelectTargetDialog(QDialog):
    SCENES_TAB = 0
    ANNOTATIONS_TAB = 1
    PHYS_OBJS_TAB = 2

    def __init__(self, scenes_model, parent=None):
        super().__init__(parent)

        self.scene = None
        self.scenes_model = scenes_model
        self.scenes_list = None
        self.annotations_list = None
        self.phys_objs_list = None

        # the selected item in lists
        self.current_text = None
        self.event_target = None

        self.setup_ui()

    def set_target_types(self, event_type, target_types):
        if self.scene is None:
            logger.warning("The scene is not set for select event target dialog. Return.")
            return

        self.scenes_list.clear()
        self.annotations_list.clear()
        self.phys_objs_list.clear()

        if len(target_types) == 1:
            target_type = target_types[0]
            if issubclass(target_type, Annotation):
                all_scene_annotations = self.scene.get_all_annotations()
                for annotation in all_scene_annotations:
                    if isinstance(annotation, target_type):
                        self.annotations_list.addItem(annotation.name)

                self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, True);
                self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, False);
            elif target_type == Scene:
                scenes = self.scenes_model.get_all_scenes()
                for scene in scenes:
                    self.scenes_list.addItem(scene.name)

                self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, True);
                self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, False);
            elif target_type == PhysicalObject:
                phys_objs = self.scene.get_physical_objects()
                for phys_obj in phys_objs:
                    self.phys_objs_list.addItem(phys_obj.name)

                self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, False);
                self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, True);
        elif len(target_types) == 2:
            all_scene_annotations = self.scene.get_all_annotations()
            for annotation in all_scene_annotations:
                if event_type == SelectionEvent:
                    if annotation.is_selectable:
                        self.annotations_list.addItem(annotation.name)
                else:
                    self.annotations_list.addItem(annotation.name)

            phys_objs = self.scene.get_physical_objects()
            for phys_obj in phys_objs:
                self.phys_objs_list.addItem(phys_obj.name)

            self.tabWidget.setTabEnabled(SelectTargetDialog.SCENES_TAB, False);
            self.tabWidget.setTabEnabled(SelectTargetDialog.ANNOTATIONS_TAB, True);
            self.tabWidget.setTabEnabled(SelectTargetDialog.PHYS_OBJS_TAB, True);

    def get_event_target(self):
        if self.tabWidget.currentIndex() == SelectTargetDialog.SCENES_TAB:
            self.event_target = self.event_target = self.scenes_model.get_scene_by_name(self.current_text)
        elif self.tabWidget.currentIndex() == SelectTargetDialog.ANNOTATIONS_TAB:
            self.event_target = self.scene.get_annotation_by_name(self.current_text)
        else:
            self.event_target = self.scene.get_physical_object_by_name(self.current_text)

        return self.event_target

    def target_list_current_text_changed(self, current_text):
        self.current_text = current_text

    def setup_ui(self):
        uic.loadUi("isar/ui/select_event_target_dialog.ui", self)
        self.scenes_list.currentTextChanged.connect(self.target_list_current_text_changed)
        self.annotations_list.currentTextChanged.connect(self.target_list_current_text_changed)
        self.phys_objs_list.currentTextChanged.connect(self.target_list_current_text_changed)



