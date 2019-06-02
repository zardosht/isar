from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene


class Event:
    # if an event has extra properties, it must set this to true,
    # and give an implementation for update_event_properties_frame(qt_frame)
    has_properties = False

    # each type of event must define its target types.
    target_types = None

    def __init__(self, target):
        self.scene_id = None
        self.name = None
        self.target = target

    @classmethod
    def update_event_properties_frame(cls, qt_frame):
        pass


class SelectionEvent(Event):
    from isar.scene.annotationmodel import Annotation
    target_types = [PhysicalObject, Annotation]

    trigger_interval = 0.2
    """
    Defines the interval before firing selection events. Added to prevent immediate firing of the event
    as the user moves the selection tool on top of different annotations and objects 
    """

    repeat_interval = 1
    """
    Interval between repeated sending of the event. 
    """

    pass


class CheckboxCheckedEvent(Event):
    from isar.scene.annotationmodel import CheckboxAnnotation
    target_types = [CheckboxAnnotation]

    def __init__(self, target):
        super().__init__(target)


class CheckboxUncheckedEvent(Event):
    from isar.scene.annotationmodel import CheckboxAnnotation
    target_types = [CheckboxAnnotation]

    def __init__(self, target):
        super().__init__(target)


class TimerFinishedEvent(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, target):
        super().__init__(target)


class TimerTimeout1Event(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTimeout2Event(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTimeout3Event(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTickEvent(Event):
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]

    def __init__(self, target, current_time):
        super().__init__(target)
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


class SceneShownEvent(Event):
    target_types = [Scene]

    pass


event_types = {
    SelectionEvent.__name__: SelectionEvent,
    CheckboxCheckedEvent.__name__: CheckboxCheckedEvent,
    TimerFinishedEvent.__name__: TimerFinishedEvent,
    TimerTimeout1Event.__name__: TimerTimeout1Event,
    TimerTimeout2Event.__name__: TimerTimeout2Event,
    TimerTimeout3Event.__name__: TimerTimeout3Event,
    TimerTickEvent.__name__: TimerTickEvent,
    PhysicalObjectAppearedEvent.__name__: PhysicalObjectAppearedEvent,
    PhysicalObjectDisappearedEvent.__name__: PhysicalObjectDisappearedEvent,
    PhysicalObjectPickedEvent.__name__: PhysicalObjectPickedEvent,
    SceneShownEvent.__name__: SceneShownEvent
}
