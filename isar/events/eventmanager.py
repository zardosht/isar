import logging
import time
from threading import Thread

from isar.events.events import TimerTickEvent, TimerTimeout1Event, TimerTimeout2Event, TimerTimeout3Event, \
    TimerFinishedEvent, CheckboxCheckedEvent, CheckboxUncheckedEvent, SelectionEvent, HandOnTopEvent, SceneShownEvent, \
    PhysicalObjectAppearedEvent, PhysicalObjectDisappearedEvent, SceneLeftEvent, PhysicalObjectPickedEvent

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
        # t = Thread(target=listener.on_event, args=(event, ))
        # t.start()

        listener.on_event(event)


def fire_timer_tick_event(timer_annotation, current_time, scene_id):
    timer_tick_event = TimerTickEvent(current_time)
    timer_tick_event.target = timer_annotation
    timer_tick_event.scene_id = scene_id
    fire_event(timer_tick_event)


def fire_timer_timeout1_event(timer_annotation, current_time, scene_id):
    timer_timeout1_event = TimerTimeout1Event(current_time)
    timer_timeout1_event.target = timer_annotation
    timer_timeout1_event.scene_id = scene_id
    fire_event(timer_timeout1_event)


def fire_timer_timeout2_event(timer_annotation, current_time, scene_id):
    timer_timeout2_event = TimerTimeout2Event(current_time)
    timer_timeout2_event.target = timer_annotation
    timer_timeout2_event.scene_id = scene_id
    fire_event(timer_timeout2_event)


def fire_timer_timeout3_event(timer_annotation, current_time, scene_id):
    timer_timeout3_event = TimerTimeout3Event(current_time)
    timer_timeout3_event.target = timer_annotation
    timer_timeout3_event.scene_id = scene_id
    fire_event(timer_timeout3_event)


def fire_timer_finished_event(timer_annotation, scene_id):
    timer_finished_event = TimerFinishedEvent()
    timer_finished_event.target = timer_annotation
    timer_finished_event.scene_id = scene_id
    fire_event(timer_finished_event)


def fire_checkbox_checked_event(checkbox_annotation, scene_id):
    checked_event = CheckboxCheckedEvent()
    checked_event.target = checkbox_annotation
    checked_event.scene_id = scene_id
    fire_event(checked_event)


def fire_checkbox_unchecked_event(checkbox_annotation, scene_id):
    unchecked_event = CheckboxUncheckedEvent()
    unchecked_event.target = checkbox_annotation
    unchecked_event.scene_id = scene_id
    fire_event(unchecked_event)


def fire_checkbox_group_checked_event(checkbox_group_checked_event):
    fire_event(checkbox_group_checked_event)


def fire_checkbox_group_unchecked_event(checkbox_group_unchecked_event):
    fire_event(checkbox_group_unchecked_event)


def fire_selection_event(target, scene_id):
    selection_event = SelectionEvent()
    selection_event.target = target
    selection_event.scene_id = scene_id
    fire_event(selection_event)


def fire_hand_on_top_event(target, scene_id):
    hand_on_top_event = HandOnTopEvent()
    hand_on_top_event.target = target
    hand_on_top_event.scene_id = scene_id
    fire_event(hand_on_top_event)


def fire_scene_shown_event(scene, scene_id):
    scene_shown_event = SceneShownEvent()
    scene_shown_event.target = scene
    scene_shown_event.scene_id = scene_id
    fire_event(scene_shown_event)


def fire_scene_left_event(scene, scene_id):
    scene_shown_event = SceneLeftEvent()
    scene_shown_event.target = scene
    scene_shown_event.scene_id = scene_id
    fire_event(scene_shown_event)


def fire_physical_object_appeared_event(phys_obj, scene_id):
    object_appeared_event = PhysicalObjectAppearedEvent()
    object_appeared_event.target = phys_obj
    object_appeared_event.scene_id = scene_id
    fire_event(object_appeared_event)


def fire_physical_object_disappeared_event(phys_obj, scene_id):
    object_disappeared_event = PhysicalObjectDisappearedEvent()
    object_disappeared_event.target = phys_obj
    object_disappeared_event.scene_id = scene_id
    fire_event(object_disappeared_event)


def fire_physical_object_picked_event(phys_obj, scene_id):
    logger.info("Physical object picked: {}", phys_obj)

    object_picked_event = PhysicalObjectPickedEvent()
    object_picked_event.target = phys_obj
    object_picked_event.scene_id = scene_id
    fire_event(object_picked_event)


def fire_physical_object_group_appeared_event(obj_group_appeared_event):
    fire_event(obj_group_appeared_event)
