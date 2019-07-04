import logging

from PyQt5.QtWidgets import QPushButton, QLabel, QDialog

from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene


logger = logging.getLogger("isar.events.events")


class Event:
    # if an event has extra properties, it must set this to true,
    # and give an implementation for update_event_properties_frame(qt_frame)
    has_properties = False

    # each type of event must define its target types.
    target_types = None

    has_multiple_targets = False

    def __init__(self):
        self.scene_id = None
        self.name = None
        self._target = None
        # for the case the event has multiple targets
        self._targets = None

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, value):
        if not isinstance(value, list):
            logger.error("targets is not List! Return.")
            return

        self._targets = value

    @classmethod
    def update_event_properties_frame(cls, qt_frame):
        pass

    def __hash__(self):
        if self.has_multiple_targets:
            if self._targets is not None and isinstance(self._targets, list) and len(self._targets) > 0:
                return hash(str(self._targets))
            else:
                return id(self)
        else:
            if self._target is not None:
                return hash(self._target.name)
            else:
                return id(self)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        if self.scene_id != other.scene_id:
            return False

        if not self.has_multiple_targets:
            return self._target.name == other.target.name
        else:
            if self._targets is None or other.targets is None:
                return False
            if type(self._targets) != list or type(other.targets) != list:
                return False

            if len(self._targets) != len(other.targets):
                return False

            other_target_names = [target.name for target in other.targets]
            for target in self._targets:
                if target.name not in other_target_names:
                    return False

            return True


class SelectionEvent(Event):
    from isar.scene.annotationmodel import Annotation
    target_types = [PhysicalObject, Annotation]

    trigger_interval = 0.2
    """
    Defines the interval before firing selection events. Added to prevent immediate firing of the event
    as the user moves the selection tool on top of different annotations and objects 
    """

    repeat_interval = 100000000
    """
    Interval between repeated sending of the event. SelectionEvent is not repeatable, i.e. interval = very large 
    """

    pass


class CheckboxCheckedEvent(Event):
    from isar.scene.annotationmodel import CheckboxAnnotation
    target_types = [CheckboxAnnotation]

    pass


class CheckboxUncheckedEvent(Event):
    from isar.scene.annotationmodel import CheckboxAnnotation
    target_types = [CheckboxAnnotation]

    pass


class CheckboxGroupCheckedEvent(Event):
    from isar.scene.annotationmodel import CheckboxAnnotation
    target_types = [CheckboxAnnotation]
    has_multiple_targets = True

    pass


class CheckboxGroupUncheckedEvent(Event):
    from isar.scene.annotationmodel import CheckboxAnnotation
    target_types = [CheckboxAnnotation]
    has_multiple_targets = True

    pass


class TimerFinishedEvent(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    pass


class TimerTimeout1Event(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, current_time):
        super().__init__()
        self.current_time = current_time


class TimerTimeout2Event(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, current_time):
        super().__init__()
        self.current_time = current_time


class TimerTimeout3Event(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, current_time):
        super().__init__()
        self.current_time = current_time


class TimerTickEvent(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, current_time):
        super().__init__()
        self.current_time = current_time


class PhysicalObjectAppearedEvent(Event):
    target_types = [PhysicalObject]
    pass


class PhysicalObjectDisappearedEvent(Event):
    target_types = [PhysicalObject]
    pass


class PhysicalObjectPickedEvent(Event):
    target_types = [PhysicalObject]
    pass


class PhysicalObjectGroupAppearedEvent(Event):
    target_types = [PhysicalObject]
    has_multiple_targets = True

    pass


class PhysicalObjectPlacedInAreaEvent(Event):
    from isar.scene.annotationmodel import ObjectAreaAnnotation
    target_types = [ObjectAreaAnnotation]

    has_properties = True

    physical_object = None

    @classmethod
    def update_event_properties_frame(cls, scene, select_target_dialog, qt_frame):
        layout = qt_frame.layout()
        for i in reversed(range(layout.count())):
            widget_to_remove = layout.itemAt(i).widget()
            layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

        select_phys_obj_btn = QPushButton()
        select_phys_obj_btn.setText("Select Physical Object ...")
        layout.addWidget(select_phys_obj_btn)

        phys_obj_label = QLabel()
        phys_obj_label.setWordWrap(True)
        layout.addWidget(phys_obj_label)

        select_phys_obj_btn.clicked.connect(lambda: cls.show_select_target_dialog(
                                               scene, select_target_dialog, phys_obj_label))

    @classmethod
    def show_select_target_dialog(cls, scene, select_target_dialog, phys_obj_label):
        cls.physical_object = None
        select_target_dialog.scene = scene
        select_target_dialog.set_target_types(PhysicalObject)
        select_target_dialog.setModal(True)
        select_target_dialog.exec()
        if select_target_dialog.result() == QDialog.Accepted:
            targets = select_target_dialog.get_targets()
            if not len(targets) > 0:
                return

            cls.physical_object = targets[0]
            phys_obj_label.setText(cls.physical_object.name)

    @classmethod
    def reset_properties(cls):
        cls.physical_object = None

    @classmethod
    def set_properties(cls, instance):
        instance.physical_object = cls.physical_object


class PhysicalObjectRemovedFromAreaEvent(PhysicalObjectPlacedInAreaEvent):
    pass


class SceneShownEvent(Event):
    # Delay before executing actions that depend on this event in a rule. This is added to make sure
    # the scene is rendered and then the corresponding actions are performed.
    delay = 0.6
    target_types = [Scene]
    pass


class SceneLeftEvent(Event):
    target_types = [Scene]
    pass


class HandOnTopEvent(SelectionEvent):
    trigger_interval = 0.2
    repeat_interval = 0.5
    pass


event_types = {
    SelectionEvent.__name__: SelectionEvent,

    CheckboxCheckedEvent.__name__: CheckboxCheckedEvent,
    CheckboxUncheckedEvent.__name__: CheckboxUncheckedEvent,
    CheckboxGroupCheckedEvent.__name__: CheckboxGroupCheckedEvent,
    CheckboxGroupUncheckedEvent.__name__: CheckboxGroupUncheckedEvent,

    TimerFinishedEvent.__name__: TimerFinishedEvent,
    TimerTimeout1Event.__name__: TimerTimeout1Event,
    TimerTimeout2Event.__name__: TimerTimeout2Event,
    TimerTimeout3Event.__name__: TimerTimeout3Event,
    TimerTickEvent.__name__: TimerTickEvent,

    PhysicalObjectAppearedEvent.__name__: PhysicalObjectAppearedEvent,
    PhysicalObjectDisappearedEvent.__name__: PhysicalObjectDisappearedEvent,
    PhysicalObjectPickedEvent.__name__: PhysicalObjectPickedEvent,
    PhysicalObjectGroupAppearedEvent.__name__: PhysicalObjectGroupAppearedEvent,
    PhysicalObjectPlacedInAreaEvent.__name__: PhysicalObjectPlacedInAreaEvent,
    PhysicalObjectRemovedFromAreaEvent.__name__: PhysicalObjectRemovedFromAreaEvent,

    SceneShownEvent.__name__: SceneShownEvent,
    SceneLeftEvent.__name__: SceneLeftEvent
}
