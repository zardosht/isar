import logging
from threading import Thread

from isar.events.actions import StartAnimationAction, StopAnimationAction
from isar.scene.annotationmodel import CurveAnnotation, TimerAnnotation, in_circle, FeedbackAnnotation, \
    AnimationAnnotation, CounterAnnotation

"""
Defining the exercises: FollowThePath, CatchTheObjects
"""


logger = logging.getLogger("isar.handskilllearning.handskill_exercise_model")


class HandSkillExercise:
    def __init__(self):
        self.name = None
        self.scene = None
        self.running = False
        self.feedback = Feedback()
        self.hasCounterAnnotation = False

    def get_scene(self):
        return self.scene

    def set_scene(self, value):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")

    def get_feedback(self):
        return self.feedback

    def set_feedback(self):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")

    def start(self):
        pass

    def stop(self):
        pass


class FollowThePathExercise(HandSkillExercise):
    def __init__(self):
        super().__init__()
        self.error = Error()
        self.time = Time()
        self.captured_points = set()
        self.selection_stick = None

    def get_error(self):
        return self.error

    def set_error(self, value):
        self.error = value

    def get_time(self):
        return self.time

    def set_time(self, value):
        self.time = value

    def set_scene(self, value):
        self.scene = value
        curves = self.scene.get_all_annotations_by_type(CurveAnnotation)
        curves[0].exercise = self

    def set_feedback(self, value):
        self.feedback = value

    def start(self):
        if not self.running:
            logger.info("Start follow the path exercise")
            self.running = True

            curve_annotations = self.scene.get_all_annotations_by_type(CurveAnnotation)
            curve_annotations[0].show_feedback = True
            for point in curve_annotations[0].line_points_distributed:
                point.set_hit(False)

            timer_annotations = self.scene.get_all_annotations_by_type(TimerAnnotation)
            timer_annotations[0].add_timer_finished_listener(self)
            timer_annotations[0].start()

            feedback_annotations = self.scene.get_all_annotations_by_type(FeedbackAnnotation)
            feedback_annotations[0].set_show_inactive(True)

            counter_annotations = self.scene.get_all_annotations_by_type(CounterAnnotation)
            counter_annotations[0].current_number = 0

            collect_points_thread = Thread(name="CollectPointsThread", target=self.start_collect_points)
            collect_points_thread.daemon = True
            collect_points_thread.start()

    def start_collect_points(self):
        curve_annotations = self.scene.get_all_annotations_by_type(CurveAnnotation)
        counter_annotations = self.scene.get_all_annotations_by_type(CounterAnnotation)
        while True:
            if not self.running:
                break
            stick_point = self.selection_stick.get_center_point(in_image_coordinates=False)
            if stick_point is not None:
                for point in curve_annotations[0].line_points_distributed:
                    if in_circle(stick_point, point.get_point(), CurveAnnotation.RADIUS):
                        self.captured_points.add(point.get_point())
                        point.set_hit(True)
                        if self.hasCounterAnnotation:
                            counter_annotations[0].current_number = len(self.captured_points)

    def on_timer_finished(self):
        if self.running:
            self.stop()

    def stop(self):
        if self.running:
            logger.info("Stop follow the path exercise")
            self.running = False
            timer_annotations = self.scene.get_all_annotations_by_type(TimerAnnotation)
            timer_annotations[0].stop()
            timer_annotations[0].reset()

            number_captured = len(self.captured_points)
            feedback_annotations = self.scene.get_all_annotations_by_type(FeedbackAnnotation)
            target_number_points = self.feedback.get_target_value()

            if number_captured >= (self.feedback.get_good() * target_number_points)/100:
                feedback_annotations[0].set_show_good(True)
            elif number_captured >= (self.feedback.get_average() * target_number_points)/100:
                feedback_annotations[0].set_show_average(True)
            elif number_captured >= (self.feedback.get_bad() * target_number_points)/100:
                feedback_annotations[0].set_show_bad(True)
            else:
                feedback_annotations[0].set_show_inactive(True)


class CatchTheObjectExercise(HandSkillExercise):
    def __init__(self):
        super().__init__()
        self.number = Number()
        self.time = Time()
        self.number_captured = 0

    def get_number(self):
        return self.number

    def set_number(self, value):
        self.number = value

    def get_time(self):
        return self.time

    def set_time(self, value):
        self.time = value

    def set_scene(self, value):
        self.scene = value

        # start the exercise from the actions
        scene_actions = self.scene.get_actions()
        for action in scene_actions:
            if isinstance(action, StartAnimationAction):
                start_animation_action = action
            if isinstance(action, StopAnimationAction):
                stop_animation_action = action

        start_animation_action.exercise = self
        stop_animation_action.exercise = self

    def set_feedback(self, value):
        self.feedback = value

    def start(self):
        if not self.running:
            logger.info("Start catch the object exercise")
            self.number_captured = 0
            self.running = True

            timer_annotations = self.scene.get_all_annotations_by_type(TimerAnnotation)
            timer_annotations[0].add_timer_finished_listener(self)
            timer_annotations[0].start()

            feedback_annotations = self.scene.get_all_annotations_by_type(FeedbackAnnotation)
            feedback_annotations[0].set_show_inactive(True)

            # start all animation threads
            animation_annotations = self.scene.get_all_annotations_by_type(AnimationAnnotation)
            for animation in animation_annotations:
                animation.start()

    def on_timer_finished(self):
        if self.running:
            self.stop()

    def stop(self):
        if self.running:
            logger.info("Stop catch the object exercise")
            self.running = False
            timer_annotations = self.scene.get_all_annotations_by_type(TimerAnnotation)
            timer_annotations[0].stop()
            timer_annotations[0].reset()

            # stop all animation threads
            animation_annotations = self.scene.get_all_annotations_by_type(AnimationAnnotation)
            for animation in animation_annotations:
                if not animation.image_shown:
                    self.number_captured = self.number_captured + 1
                animation.stop()

            feedback_annotations = self.scene.get_all_annotations_by_type(FeedbackAnnotation)
            target_number = self.feedback.get_target_value()

            if self.number_captured >= (self.feedback.get_good() * target_number)/100:
                feedback_annotations[0].set_show_good(True)
            elif self.number_captured >= (self.feedback.get_average() * target_number)/100:
                feedback_annotations[0].set_show_average(True)
            elif self.number_captured >= (self.feedback.get_bad() * target_number)/100:
                feedback_annotations[0].set_show_bad(True)
            else:
                feedback_annotations[0].set_show_inactive(True)


"""
Defining the feedback for the exercise
"""


class Feedback:
    def __init__(self):
        self.target_value = None
        self.good = None
        self.average = None
        self.bad = None

    def get_target_value(self):
        return self.target_value

    def set_target_value(self, value):
        self.target_value = value

    def get_good(self):
        return self.good

    def set_good(self, value):
        self.good = value

    def get_average(self):
        return self.average

    def set_average(self, value):
        self.average = value

    def get_bad(self):
        return self.bad

    def set_bad(self, value):
        self.bad = value


"""
Defining the evaluation aspects: Error, Time
"""


class EvaluationAspect:
    def __init__(self):
        self.beginner = Beginner()
        self.intermediate = Intermediate()
        self.competent = Competent()

    def get_beginner(self):
        return self.beginner

    def set_beginner(self, value):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")

    def get_intermediate(self):
        return self.intermediate

    def set_intermediate(self, value):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")

    def get_competent(self):
        return self.beginner

    def set_competent(self, value):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")


class Error(EvaluationAspect):

    def __init__(self):
        super().__init__()

    def set_beginner(self, value):
        self.beginner = value

    def set_intermediate(self, value):
        self.intermediate = value

    def set_competent(self, value):
        self.competent = value


class Time(EvaluationAspect):

    def __init__(self):
        super().__init__()

    def set_beginner(self, value):
        self.beginner = value

    def set_intermediate(self, value):
        self.intermediate = value

    def set_competent(self, value):
        self.competent = value


class Number(EvaluationAspect):

    def __init__(self):
        super().__init__()

    def set_beginner(self, value):
        self.beginner = value

    def set_intermediate(self, value):
        self.intermediate = value

    def set_competent(self, value):
        self.competent = value


"""
Defining the skill levels: Beginner, Intermediate, Competent
"""


class SkillLevel:
    def __init__(self):
        self.value = None

    def get_value(self):
        return self.value

    def set_value(self, value):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")


class Beginner(SkillLevel):
    def __init__(self):
        super().__init__()

    def set_value(self, value):
        self.value = value


class Intermediate(SkillLevel):
    def __init__(self):
        super().__init__()

    def set_value(self, value):
        self.value = value


class Competent(SkillLevel):
    def __init__(self):
        super().__init__()

    def set_value(self, value):
        self.value = value
