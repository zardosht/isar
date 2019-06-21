import logging

from PyQt5 import uic, Qt, QtCore
from PyQt5.QtCore import QAbstractListModel, QModelIndex
from PyQt5.QtWidgets import QDialog, QListWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QWidget

from isar.events import events, actions
from isar.events.actions import Action, ToggleAnnotationVisibilityAction
from isar.events.events import SelectionEvent, Event
from isar.events.rules import Rule
from isar.events.select_target_dialog import SelectTargetDialog
from isar.scene.annotationmodel import Annotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.scene.events_actions_rules")


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

        self.select_target_dialog = SelectTargetDialog(self.scenes_model, parent=self)

        self.events_scene = None
        self.event_type = None
        self.event_target = None
        self.event_name = None
        self.event = None
        self.scenes_combo_current_index_changed(0, "event_scenes_combo")
        self.event_type_combo_current_index_changed(0)

        self.actions_scene = None
        self.action_type = None
        self.action_target = None
        self.action_name = None
        self.action = None
        self.scenes_combo_current_index_changed(0, "action_scenes_combo")
        self.action_type_combo_current_index_changed(0)

        self.rules_scene = None
        self.rule_name = None
        self.rule_event = None
        self.rule_action = None
        self.rule = None
        self.scenes_combo_current_index_changed(0, "rule_scenes_combo")

    def init_ui(self):
        uic.loadUi("isar/ui/events_actions_rules_dialog.ui", self)

        self.event_properties_frame.hide()

        self.init_scenes_combos()
        self.init_event_type_combo()
        self.init_action_type_combo()

        self.select_scene_event_target_btn.clicked.connect(
            lambda: self.select_event_target_btn_clicked(Scene))
        self.select_annotation_event_target_btn.clicked.connect(
            lambda: self.select_event_target_btn_clicked(Annotation))
        self.select_phys_obj_event_target_btn.clicked.connect(
            lambda: self.select_event_target_btn_clicked(PhysicalObject))

        self.select_scene_action_target_btn.clicked.connect(
            lambda: self.select_action_target_btn_clicked(Scene))
        self.select_annotation_action_target_btn.clicked.connect(
            lambda: self.select_action_target_btn_clicked(Annotation))
        self.select_phys_obj_action_target_btn.clicked.connect(
            lambda: self.select_action_target_btn_clicked(PhysicalObject))

        self.add_event_btn.clicked.connect(self.add_event_btn_clicked)
        self.remove_event_btn.clicked.connect(self.remove_event_btn_clicked)
        self.event_name_text.textChanged.connect(self.event_name_text_changed)
        
        self.add_action_btn.clicked.connect(self.add_action_btn_clicked)
        self.remove_action_btn.clicked.connect(self.remove_action_btn_clicked)
        self.action_name_text.textChanged.connect(self.action_name_text_changed)

        self.select_rule_event_btn.clicked.connect(self.select_rule_event_btn_clicked)
        self.select_rule_action_btn.clicked.connect(self.select_rule_action_btn_clicked)

        self.add_rule_btn.clicked.connect(self.add_rule_btn_clicked)
        self.remove_rule_btn.clicked.connect(self.remove_rule_btn_clicked)
        self.rule_name_text.textChanged.connect(self.rule_name_text_changed)

    def add_action_btn_clicked(self):
        if self.action_type.has_target:
            if not self.action_type.is_action_target_valid(self.action_target):
                logger.error("Action target is not valid. Return.")
                return

        if self.actions_scene is None:
            logger.error("self.actions_scene is None. Return.")

        if self.action is None:
            self.action = self.action_type()
            self.action.set_target(self.action_target)
            self.action.name = self.action_name
            self.action.scene_id = self.actions_scene.name
            if self.action_type.has_properties:
                self.action_type.set_properties(self.action)

            self.actions_model.add_item(self.action)

            # reset form
            self.action = None
            self.action_name = None
            self.action_name_text.setText("")
            self.action_target_label.show()
            self.action_target_label.setText("... select action target(s) ...")
            self.action_type = None
            self.action_type_combo.setCurrentIndex(0)
            self.action_type_combo_current_index_changed(0)
            self.action_name = None
            self.action_name_text.setText("")

    def event_name_text_changed(self, text):
        self.event_name = text
        
    def action_name_text_changed(self, text):
        self.action_name = text
        
    def rule_name_text_changed(self, text):
        self.rule_name = text

    def remove_action_btn_clicked(self):
        index = self.actions_list.selectionModel().currentIndex()
        self.actions_model.remove_item(index)

    def add_rule_btn_clicked(self):
        if self.rule_event is None:
            logger.error("self.rule_event is None. Return.")
            return
        
        if self.rule_action is None:
            logger.error("self.rule_action is None. Return.")
            return

        if self.rule_name is None or len(self.rule_name) == 0:
            logger.error("self.rule_name is None or empty. Return.")
            return

        if self.rule is None:
            self.rule = Rule()
            self.rule.scene = self.rules_scene
            self.rule.name = self.rule_name
            self.rule.event = self.rule_event
            self.rule.action = self.rule_action
            self.rules_model.add_item(self.rule)

            self.rule = None
            self.rule_name = None
            self.rule_name_text.setText("")
            self.rule_event = None
            self.rule_event_name_label.setText("... select event ...")
            self.rule_action = None
            self.rule_action_name_label.setText("... select action ...")

    def remove_rule_btn_clicked(self):
        index = self.rules_list.selectionModel().currentIndex()
        self.rules_model.remove_item(index)

    def select_rule_event_btn_clicked(self):
        if self.rules_scene is None:
            logger.error("self.rules_scene is None. Return.")
            return

        selected_events = self.show_select_target_dialog(Event, self.rules_scene)
        if selected_events is not None and len(selected_events) > 0:
            self.rule_event = selected_events[0]
            self.rule_event_name_label.setText(self.rule_event.name)
            if self.rule_action is not None:
                self.rule_name_text.setText("{}__{}".format(self.rule_event.name, self.rule_action.name))

    def select_rule_action_btn_clicked(self):
        if self.rules_scene is None:
            logger.error("self.rules_scene is None. Return.")
            return

        selected_actions = self.show_select_target_dialog(Action, self.rules_scene)
        if selected_actions is not None and len(selected_actions) > 0:
            self.rule_action = selected_actions[0]
            self.rule_action_name_label.setText(self.rule_action.name)
            if self.rule_event is not None:
                self.rule_name_text.setText("{}__{}".format(self.rule_event.name, self.rule_action.name))

    def add_event_btn_clicked(self):
        if self.event_target is None:
            logger.warning("self.event_target is None. Return.")
            return

        if self.events_scene is None:
            logger.warning("self.events_scene is None. Return.")
            return

        if self.event is None:
            if isinstance(self.event_target, list):
                self.event = self.event_type()
                self.event.targets = self.event_target
            else:
                self.event = self.event_type()
                self.event.target = self.event_target

            self.event.name = self.event_name
            self.event.scene_id = self.events_scene.name
            self.events_model.add_item(self.event)

            # reset form
            self.event = None
            self.event_type = None
            self.event_type_combo.setCurrentIndex(0)
            self.event_type_combo_current_index_changed(0)
            self.event_target = None
            self.event_name = None
            self.event_name_text.setText("")
            self.event_target_label.setText("... select event target ...")

    def remove_event_btn_clicked(self):
        index = self.events_list.selectionModel().currentIndex()
        self.events_model.remove_item(index)

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
            self.events_model.set_current_scene(scene)
            self.events_scene = scene

            self.event = None
            self.event_type = None
            self.event_type_combo.setCurrentIndex(0)
            self.event_type_combo_current_index_changed(0)
            self.event_target = None
            self.event_name = None
            self.event_name_text.setText("")
            self.event_target_label.setText("... select event target ...")

        elif self.action_scenes_combo.objectName() == combo_name:
            scene = self.action_scenes_combo.itemData(index)
            self.actions_model.set_current_scene(scene)
            self.actions_scene = scene

            self.action = None
            self.action_type = None
            self.action_type_combo_current_index_changed(0)
            self.action_name = None
            self.action_name_text.setText("")

        elif self.rule_scenes_combo.objectName() == combo_name:
            scene = self.rule_scenes_combo.itemData(index)
            self.rules_model.set_current_scene(scene)
            self.rules_scene = scene
            self.rule_name_text.setText("")
            self.rule_event = None
            self.rule_event_name_label.setText(".... event name ...")
            self.rule_action = None
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
        event_target_types = self.event_type.target_types
        self.disable_all_event_target_selection_buttons()
        for target_type in event_target_types:
            if target_type == Scene:
                self.select_scene_event_target_btn.setEnabled(True)
            elif target_type == PhysicalObject:
                self.select_phys_obj_event_target_btn.setEnabled(True)
            else:
                self.select_annotation_event_target_btn.setEnabled(True)

    def disable_all_event_target_selection_buttons(self):
        self.select_scene_event_target_btn.setEnabled(False)
        self.select_annotation_event_target_btn.setEnabled(False)
        self.select_phys_obj_event_target_btn.setEnabled(False)

    def update_event_properties_frame(self, event_type):
        if event_type.has_properties:
            self.event_properties_frame.show()
            event_type.update_event_properties_frame(self.event_properties_frame)
        else:
            self.event_properties_frame.hide()

    def init_action_type_combo(self):
        for ac_name, ac_type in actions.scene_action_types.items():
            self.action_type_combo.addItem(ac_name, ac_type)

        for ac_name, ac_type in actions.global_action_types.items():
            self.action_type_combo.addItem(ac_name, ac_type)

        self.action_type_combo.currentIndexChanged.connect(self.action_type_combo_current_index_changed)

    def action_type_combo_current_index_changed(self, index):
        self.action = None
        self.action_name = None
        self.action_name_text.setText("")
        self.action_target_label.show()
        self.action_target_label.setText("... select action target(s) ...")
        self.action_type = self.action_type_combo.itemData(index)

        self.disable_all_action_target_selection_buttons()

        self.update_action_properties_frame(self.action_type)

        if self.action_type.has_target:
            action_target_types = self.action_type.target_types
            for target_type in action_target_types:
                if target_type == Scene:
                    self.select_scene_action_target_btn.setEnabled(True)
                elif target_type == PhysicalObject:
                    self.select_phys_obj_action_target_btn.setEnabled(True)
                else:
                    self.select_annotation_action_target_btn.setEnabled(True)
        else:
            self.action_target_label.hide()

    def update_action_properties_frame(self, action_type):
        if action_type.has_properties:
            self.action_properties_frame.show()
            action_type.update_action_properties_frame(self.actions_scene,
                                                       self.select_target_dialog,
                                                       self.action_properties_frame)
            action_type.reset_properties()
        else:
            self.action_properties_frame.hide()

    def disable_all_action_target_selection_buttons(self):
        self.select_scene_action_target_btn.setEnabled(False)
        self.select_annotation_action_target_btn.setEnabled(False)
        self.select_phys_obj_action_target_btn.setEnabled(False)

    def select_action_target_btn_clicked(self, target_type):
        if self.action_type is None:
            logger.warning("self.action_type is None. Setting to default ToggleAnnotationVisibilityAction")
            self.action_type = ToggleAnnotationVisibilityAction

        if len(self.action_type.target_types) == 1:
            target_type = self.action_type.target_types[0]

        targets = self.show_select_target_dialog(target_type,
                                                 self.actions_scene,
                                                 action_type=self.action_type)

        if targets is not None and len(targets) > 0:
            if self.action_type.has_single_target:
                self.action_target = targets[0]
                if isinstance(self.action_target, Annotation):
                    self.action_target_label.setText(self.actions_scene.name + "." + self.action_target.name)
                else:
                    self.action_target_label.setText(self.action_target.name)

            else:
                self.action_target = targets
                self.action_target_label.setText(
                    str([self.actions_scene.name + "." + target.name for target in targets]))

            logger.info("received action target: {}".format(str(self.action_target)))
            if self.action_name is None or self.action_name == "":
                if type(self.action_target) == list:
                    self.action_name = self.action_type.__name__ + "_for_" + \
                                       str([str(target) for target in self.action_target])
                else:
                    self.action_name = self.action_type.__name__ + "_for_" + str(self.action_target)

                self.action_name_text.setText(self.action_name)
        else:
            logger.warning("targets is none")

    def select_event_target_btn_clicked(self, target_type):
        if self.event_type is None:
            logger.warning("self.event_type is None. Setting to default SelectionEvent")
            self.event_type = SelectionEvent

        if len(self.event_type.target_types) == 1:
            target_type = self.event_type.target_types[0]

        targets = self.show_select_target_dialog(target_type, self.events_scene, event_type=self.event_type)

        if targets is not None and len(targets) > 0:
            logger.info("received event target: {}".format(str(targets)))

            if self.event_type.has_multiple_targets:
                self.event_target = targets
                self.event_target_label.setText(str([target.name for target in targets]))
                self.event_name = self.event_type.__name__ + "_for_" + \
                    str([str(target) for target in self.event_target])
            else:
                target = targets[0]
                self.event_target = target
                if self.event_name is None or self.event_name == "":
                    self.event_name = "On_" + self.event_target.name + "_" + self.event_type.__name__
                if isinstance(target, Scene):
                    self.event_target_label.setText(target.name)
                else:
                    self.event_target_label.setText(self.events_scene.name + "." + target.name)

            self.event_name_text.setText(self.event_name)

        else:
            logger.warning("target is none")

    def show_select_target_dialog(self, target_type, scene,
                                  event_type=None, action_type=None):
        targets = None
        self.select_target_dialog.scene = scene
        self.select_target_dialog.set_target_types(target_type, event_type, action_type)
        self.select_target_dialog.setModal(True)
        self.select_target_dialog.exec()
        if self.select_target_dialog.result() == QDialog.Accepted:
            targets = self.select_target_dialog.get_targets()

        return targets

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

    def set_current_scene(self, scene):
        self.current_scene = scene
        self.endResetModel()

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

    def remove_item(self, index):
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())
        item = index.internalPointer()
        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                if isinstance(item, Event):
                    self.current_scene.remove_event(item)
            elif self.item_type == ItemsModel.ACTIONS:
                if isinstance(item, Action):
                    self.current_scene.remove_action(item)
            elif self.item_type == ItemsModel.RULES:
                if isinstance(item, Rule):
                    self.current_scene.remove_rule(item)
        else:
            logger.warning("current_scene is None!")
        self.endRemoveRows()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        items = []
        if self.current_scene is not None:
            if self.item_type == ItemsModel.EVENTS:
                items = self.current_scene.get_events()
            elif self.item_type == ItemsModel.ACTIONS:
                items = self.current_scene.get_actions()
            elif self.item_type == ItemsModel.RULES:
                items = self.current_scene.get_rules()
        else:
            logger.warning("current_scene is None!")

        item = None
        if len(items) > row:
            item = items[row]
        return self.createIndex(row, 0, item)
