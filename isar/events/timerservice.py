import threading
import logging

from isar.events.events import TimerFinishedEvent, TimerTickEvent, TimerTimeout1Event, TimerTimeout2Event, \
    TimerTimeout3Event
from isar.scene.annotationmodel import TimerAnnotation
from isar.services.service import Service

logger = logging.getLogger("isar.timerservice")


class TimerService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.actions_service = None

    def on_event(self, timer_event):
        target = timer_event.target
        if target is None:
            logger.error("Target of timer_event is none. Return.")

        if not isinstance(target, TimerAnnotation):
            logger.error("Target of timer_event is not a TimerAnnotation. Return.")

        # ------------ Experimental ------------
        if isinstance(timer_event, TimerFinishedEvent):
            logger.info("Timer {} finisehd.".format(target.name))

        if isinstance(timer_event, TimerTickEvent):
            logger.info("Timer {} ticked.".format(target.name))

        if isinstance(timer_event, TimerTimeout1Event):
            logger.info("Timer {} timeout1 reached.".format(target.name))

        if isinstance(timer_event, TimerTimeout2Event):
            logger.info("Timer {} timeout2.".format(target.name))

        if isinstance(timer_event, TimerTimeout3Event):
            logger.info("Timer {} timeout3.".format(target.name))

        # --------------------------------------

    def stop(self):
        pass


