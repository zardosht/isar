import logging

from isar.events.events import TimerTickEvent, TimerTimeout1Event, TimerTimeout2Event, TimerTimeout3Event, \
    TimerFinishedEvent, CheckboxCheckedEvent, CheckboxUncheckedEvent, SelectionEvent

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


def fire_timer_tick_event(timer_annotation, current_time, scene_id):
    timer_tick_event = TimerTickEvent(timer_annotation, current_time)
    timer_tick_event.scene_id = scene_id
    fire_event(timer_tick_event)


def fire_timer_timeout1_event(timer_annotation, current_time, scene_id):
    timer_timeout1_event = TimerTimeout1Event(timer_annotation, current_time)
    timer_timeout1_event.scene_id = scene_id
    fire_event(timer_timeout1_event)


def fire_timer_timeout2_event(timer_annotation, current_time, scene_id):
    timer_timeout2_event = TimerTimeout2Event(timer_annotation, current_time)
    timer_timeout2_event.scene_id = scene_id
    fire_event(timer_timeout2_event)


def fire_timer_timeout3_event(timer_annotation, current_time, scene_id):
    timer_timeout3_event = TimerTimeout3Event(timer_annotation, current_time)
    timer_timeout3_event.scene_id = scene_id
    fire_event(timer_timeout3_event)


def fire_timer_finished_event(timer_annotation, scene_id):
    timer_finished_event = TimerFinishedEvent(timer_annotation)
    timer_finished_event.scene_id = scene_id
    fire_event(timer_finished_event)


def fire_checkbox_checked_event(checkbox_annotation, scene_id):
    checked_event = CheckboxCheckedEvent(checkbox_annotation)
    checked_event.scene_id = scene_id
    fire_event(checked_event)


def fire_checkbox_unchecked_event(checkbox_annotation, scene_id):
    unchecked_event = CheckboxUncheckedEvent(checkbox_annotation)
    unchecked_event.scene_id = scene_id
    fire_event(unchecked_event)


def fire_selection_event(target, scene_id):
    selection_event = SelectionEvent(target)
    selection_event.scene_id = scene_id
    fire_event(selection_event)




