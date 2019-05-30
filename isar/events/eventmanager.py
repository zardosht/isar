import logging

from isar.scene.annotationmodel import Annotation, CheckboxAnnotation, TimerAnnotation
from isar.scene.physicalobjectmodel import PhysicalObject
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.eventmanager")

# event listener must have an on_event(e) method.
event_listeners = {}


def register_listener(event_class_name, listener):
    if event_class_name in event_listeners:
        event_listeners[event_class_name].append(listener)
    else:
        event_listeners[event_class_name] = [listener]


def fire_event(event):
    event_class_name = event.__class__.__name__
    if event_class_name not in event_listeners:
        logger.warning("Event class is not the event registry. First register listeners for this event type.")
        return

    listeners = event_listeners[event_class_name]
    for listener in listeners:
        listener.on_event(event)


# ======================= Events ====================

class Event:
    # if an event has extra properties, it must set this to true,
    # and give an implementation for update_event_properties_frame(qt_frame)
    has_properties = False

    # each type of event must define its target types.
    target_types = None

    def __init__(self, target):
        self.scene_id = None
        self.target = target

    @staticmethod
    def update_event_properties_frame(qt_frame):
        pass


class SelectionEvent(Event):

    target_types = [PhysicalObject, Annotation]

    trigger_interval = 1
    """
    Defines the interval between firing selection events. 
    """
    pass


class CheckboxCheckedEvent(Event):
    target_types = [CheckboxAnnotation]

    def __init__(self, target):
        super().__init__(target)


class CheckboxUncheckedEvent(Event):
    target_types = [CheckboxAnnotation]

    def __init__(self, target):
        super().__init__(target)


class TimerFinishedEvent(Event):
    target_types = [TimerAnnotation]

    def __init__(self, target):
        super().__init__(target)


class TimerTimeout1Event(Event):
    target_types = [TimerAnnotation]

    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTimeout2Event(Event):
    target_types = [TimerAnnotation]

    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTimeout3Event(Event):
    target_types = [TimerAnnotation]

    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTickEvent(Event):
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
