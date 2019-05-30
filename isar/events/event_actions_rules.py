import logging

from PyQt5 import uic, Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QDialog, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QWidget

from isar.events import actionsservice, events
from isar.events.actionsservice import Action
from isar.events.events import SelectionEvent, Event
from isar.events.rulesmanager import Rule
from isar.scene.annotationmodel import Annotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.scene.physicalobjecttool")


"""

* get rid of global event, actions, and rules.
* Every event, action, or rule is defined only on one scene (the one user chooses) 
and is only available/active on this scene. 
* If the target of an event or action is an annotation, or physical object, 
only those annotations and physical objects of the selected scene can be chosen as target.

"""


class EventsActionsRulesDialog(QDialog):
    def __init__(self, scenes_model, annotations_model, phys_obj_model, parent=None):
        super().__init__(parent)

        self.scenes_model = scenes_model
        self.annotations_model = annotations_model
        self.physical_objects_model = phys_obj_model

        self.events_model = None
        self.actions_model = None
        self.rules_model = None

        self.init_ui()
        self.init_models()

        self.select_event_target_dialog = SelectTargetDialog(self.scenes_model, parent=self)

        self.events_scene = None
        self.event_type = None
        self.event_target = None
        self.event_name = None
        self.event = None
        self.scenes_combo_current_index_changed(0, "event_scenes_combo")
        self.event_type_combo_current_index_changed(0)

        self.actions_scene = None
        self.action_type = None
        self.action_name = None
        self.action = None
        self.scenes_combo_current_index_changed(0, "action_scenes_combo")

        self.rules_scene = None
        self.rule = None
        self.scenes_combo_current_index_changed(0, "rule_scenes_combo")

    def init_ui(self):
        uic.loadUi("isar/ui/events_actions_rules_dialog.ui", self)

        self.event_properties_frame.hide()

        self.init_scenes_combos()
        self.init_event_type_combo()
        self.init_action_type_combo()

        self.event_select_target_btn.clicked.connect(self.event_select_target_btn_clicked)
        self.add_event_btn.clicked.connect(self.add_event_btn_clicked)

    def add_event_btn_clicked(self):
        if self.event_target is None:
            logger.warning("self.event_target is None. Return.")
            return

        if self.events_scene is None:
            logger.warning("self.events_scene is None. Return.")
            return

        if self.event is None:
            self.event = self.event_type(self.event_target)
            self.event.name = self.event_name
            self.event.scene_id = self.events_scene.name
            self.events_model.add_item(self.event)

    def init_scenes_combos(self):
        scene_combos = [self.event_scenes_combo, self.action_scenes_combo, self.rule_scenes_combo]
        scenes = self.scenes_model.get_all_scenes()
        for combo in scene_combos:
            for scene in scenes:
                combo.addItem(scene.name, scene)

        self.event_scenes_combo.currentIndexChanged.connect(
            lambda index: self.scenes_combo_current_index_changed(index, "event_scenes_combo"))
        self.action_scenes_combo.currentIndexChanged.connect(
            lambda index: self.scenes_combo_current_index_changed(index, "action_scenes_combo"))
        self.rule_scenes_combo.currentIndexChanged.connect(
            lambda index: self.scenes_combo_current_index_changed(index, "rule_scenes_combo"))

    def scenes_combo_current_index_changed(self, index, combo_name):
        if self.event_scenes_combo.objectName() == combo_name:
            scene = self.event_scenes_combo.itemData(index)
            self.events_model.current_scene = scene
            self.events_scene = scene

            self.event = None
            self.event_type = None
            self.event_type_combo_current_index_changed(0)
            self.event_target = None
            self.event_name = None
            self.event_name_text.setText("")
            self.event_target_label.setText("... select event target ...")

        elif self.action_scenes_combo.objectName() == combo_name:
            scene = self.action_scenes_combo.itemData(index)
            self.actions_model.current_scene = scene
            self.actions_scene = scene

            self.action = None
            self.action_type = None
            self.action_type_combo_current_index_changed(0)
            self.action_name = None
            self.action_name_text.setText("")

        elif self.rule_scenes_combo.objectName() == combo_name:
            scene = self.rule_scenes_combo.itemData(index)
            self.rules_model.current_scene = scene
            self.rules_scene = scene
            self.rule_name_text.setText("")
            self.rule_event_name_label.setText(".... event name ...")
            self.rule_action_name_label.setText("... action name ...")

    def init_event_type_combo(self):
        for ev_name, ev_type in events.event_types.items():
            self.event_type_combo.addItem(ev_name, ev_type)

        self.event_type_combo.currentIndexChanged.connect(self.event_type_combo_current_index_changed)

    def event_type_combo_current_index_changed(self, index):
        self.event = None
        self.event_target = None
        self.event_name = None
        self.event_name_text.setText("")
        self.event_target_label.setText("... select event target ...")
        self.event_type = self.event_type_combo.itemData(index)
        self.update_event_properties_frame(self.event_type)

    def update_event_properties_frame(self, event_type):
        if event_type.has_properties:
            self.event_properties_frame.show()
            event_type.update_event_properties_frame(self.event_properties_frame)
        else:
            self.event_properties_frame.hide()

    def init_action_type_combo(self):
        for ac_name, ac_type in actionsservice.action_types.items():
            self.action_type_combo.addItem(ac_name, ac_type)

        self.action_type_combo.currentIndexChanged.connect(self.action_type_combo_current_index_changed)

    def action_type_combo_current_index_changed(self, index):
        self.action = None
        self.action_name = None
        self.action_name_text.setText("")

        # TODO: reset other properites of action

        self.action_type = self.action_type_combo.itemData(index)
        self.update_action_properties_frame(self.action_type)

    def update_action_properties_frame(self, action_type):
        logger.info("update_action_properties_frame")

    def event_select_target_btn_clicked(self):
        target = self.show_select_event_target_dialog()
        if target is not None:
            logger.info("received event target: {}".format(str(target)))
            self.event_target = target
            self.event_name = "On_" + self.event_target.name + "_" +  self.event_type.__name__
            self.event_name_text.setText(self.event_name)
            if isinstance(target, Scene):
                self.event_target_label.setText(target.name)
            else:
                self.event_target_label.setText(self.events_scene.name + "." + target.name)
        else:
            logger.warning("target is none")

    def show_select_event_target_dialog(self):
        target = None
        self.select_event_target_dialog.scene = self.events_scene
        self.select_event_target_dialog.set_target_types(self.event_type, self.event_type.target_types)
        self.select_event_target_dialog.setModal(True)
        self.select_event_target_dialog.exec()
        if self.select_event_target_dialog.result() == QDialog.Accepted:
            target = self.select_event_target_dialog.get_event_target()

        return target

    def init_models(self):
        self.events_model = ItemsModel(ItemsModel.EVENTS)
        self.events_list.setModel(self.events_model)

        self.actions_model = ItemsModel(ItemsModel.ACTIONS)
        self.actions_list.setModel(self.actions_model)

        self.rules_model = ItemsModel(ItemsModel.RULES)
        self.rules_list.setModel(self.rules_model)


class ItemsModel(QAbstractListModel):
    EVENTS = 0
    ACTIONS = 1
    RULES = 2

    def __init__(self, item_type):
        super().__init__()
        self.item_type = item_type
        self.current_scene = None

    def rowCount(self, parent=None):
        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                return len(self.current_scene.get_events())
            elif self.item_type == ItemsModel.ACTIONS:
                return len(self.current_scene.get_actions())
            elif self.item_type == ItemsModel.RULES:
                return len(self.current_scene.get_rules())
            else:
                return 0
        else:
            return 0

    def data(self, index, role):
        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.name
        elif role == QtCore.Qt.UserRole:
            return item

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def add_item(self, item):
        last_index = self.rowCount()
        self.beginInsertRows(QModelIndex(), last_index, last_index + 1)
        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                if isinstance(item, Event):
                    self.current_scene.add_event(item)
            elif self.item_type == ItemsModel.ACTIONS:
                if isinstance(item, Action):
                    self.current_scene.add_action(item)
            elif self.item_type == ItemsModel.RULES:
                if isinstance(item, Rule):
                    self.current_scene.add_rule(item)
        else:
            logger.warning("current_scene is None!")
        self.endInsertRows()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                items = self.current_scene.get_events()
            elif self.item_type == ItemsModel.ACTIONS:
                items = self.current_scene.get_actions()
            elif self.item_type == ItemsModel.RULES:
                items = self.current_scene.get_rules()
        else:
            logger.warning("current_scene is None!")

        item = items[row]
        return self.createIndex(row, 0, item)


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



