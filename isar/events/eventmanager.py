import logging

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
    def __init__(self, target):
        self.scene_id = None
        self.target = target


class SelectionEvent(Event):
    trigger_interval = 1
    """
    Defines the interval between firing selection events. 
    """
    pass


class CheckboxCheckedEvent(Event):
    def __init__(self, target, check_stat):
        super().__init__(target)
        self.check_state = check_stat


class TimerFinishedEvent(Event):
    def __init__(self, target):
        super().__init__(target)


class TimerTimeout1Event(Event):
    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTimeout2Event(Event):
    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTimeout3Event(Event):
    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class TimerTickEvent(Event):
    def __init__(self, target, current_time):
        super().__init__(target)
        self.current_time = current_time


class PhysicalObjectAppearedEvent(Event):
    pass


class PhysicalObjectDisappearedEvent(Event):
    pass


class PhysicalObjectPickedEvent(Event):
    pass


class SceneChangedEvent(Event):
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
    SceneChangedEvent.__name__: SceneChangedEvent
}
