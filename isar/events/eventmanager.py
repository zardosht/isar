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
        self.target = target


class SelectionEvent(Event):
    trigger_interval = 1
    """
    Defines the interval between firing selection events. 
    """
    pass


class PhysicalObjectAppearedEvent(Event):
    pass


class PhysicalObjectDisappearedEvent(Event):
    pass


class PhysicalObjectPickedEvent(Event):
    pass


class TimerFinishedEvent(Event):
    pass


class TimerTimeoutEvent(Event):
    def __init__(self):
        self.current_time = None
