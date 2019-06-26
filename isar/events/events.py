import logging

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

    # TODO: implement
    pass


class PhysicalObjectGroupAppearedEvent(Event):
    target_types = [PhysicalObject]
    has_multiple_targets = True

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

    TimerFinishedEvent.__name__: TimerFinishedEvent,
    TimerTimeout1Event.__name__: TimerTimeout1Event,
    TimerTimeout2Event.__name__: TimerTimeout2Event,
    TimerTimeout3Event.__name__: TimerTimeout3Event,
    TimerTickEvent.__name__: TimerTickEvent,

    PhysicalObjectAppearedEvent.__name__: PhysicalObjectAppearedEvent,
    PhysicalObjectDisappearedEvent.__name__: PhysicalObjectDisappearedEvent,
    PhysicalObjectPickedEvent.__name__: PhysicalObjectPickedEvent,
    PhysicalObjectGroupAppearedEvent.__name__: PhysicalObjectGroupAppearedEvent,

    SceneShownEvent.__name__: SceneShownEvent,
    SceneLeftEvent.__name__: SceneLeftEvent
}
