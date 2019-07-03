import logging

import numpy
from isar.scene.annotationmodel import CurveAnnotation, TimerAnnotation, in_circle, FeedbackAnnotation, \
    AnimationAnnotation
from threading import Thread

"""
Defining the exercises: FollowThePath, CatchTheObjects
"""


logger = logging.getLogger("isar.handskilllearning.handskill_exercise_model")


class HandSkillExercise:
    def __init__(self):
        self.name = None
        self.scene = None
        self.feedback = Feedback()
        self.selection_stick = None

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
        self.running = False
        self.register_points = []

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
            print("Start Exercise")
            self.register_points = []
            self.running = True

            timer_annotations = self.scene.get_all_annotations_by_type(TimerAnnotation)
            timer_annotations[0].start()
            timer_annotations[0].add_timer_finished_listener(self)

            feedback_annotations = self.scene.get_all_annotations_by_type(FeedbackAnnotation)
            feedback_annotations[0].set_show_inactive(True)

            collect_points_thread = Thread(target=self.start_collect_points)
            collect_points_thread.start()

    def start_collect_points(self):
        while True:
            if not self.running:
                break
            stick_point = self.selection_stick.get_center_point(in_image_coordinates=False)
            actual = self.scene.get_all_annotations_by_type(CurveAnnotation)
            if stick_point is not None:
                for point in actual[0].line_points_distributed:
                    if in_circle(stick_point, point, CurveAnnotation.RADIUS):
                        self.register_points.append(point)

    def on_timer_finished(self):
        if self.running:
            self.stop()

    def stop(self):
        if self.running:
            print("Stop Exercise")
            self.running = False
            timer_annotation = self.scene.get_all_annotations_by_type(TimerAnnotation)
            timer_annotation[0].stop()
            timer_annotation[0].reset()

            print("Captured")
            no_duplicates = numpy.unique(self.register_points, axis=0)
            number_captured = len(no_duplicates)
            print(number_captured)

            feedback_annotation = self.scene.get_all_annotations_by_type(FeedbackAnnotation)
            print("Target")
            target_number_points = self.feedback.get_target_value()
            print(target_number_points)

            if number_captured >= (self.feedback.get_good() * target_number_points)/100:
                feedback_annotation[0].set_show_good(True)
                print("FEEDBACK GOOD!!!!!!!!")
            elif number_captured >= (self.feedback.get_average() * target_number_points)/100:
                feedback_annotation[0].set_show_average(True)
                print("FEEDBACK AVERAGE!!!!!!!!")
            elif number_captured >= (self.feedback.get_good() * target_number_points)/100:
                feedback_annotation[0].set_show_bad(True)
                print("FEEDBACK BAD!!!!!!!!")
            else:
                feedback_annotation[0].set_show_inactive(True)
                print("FEEDBACK NOT EXISTING")


class CatchTheObjectExercise(HandSkillExercise):
    def __init__(self):
        super().__init__()
        self.number = Number()
        self.time = Time()
        self.running = False
        self.register_objects = []

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

        # TODO: not sure if needed for this type exercise
        animations = self.scene.get_all_annotations_by_type(AnimationAnnotation)
        animations[0].exercise = self

    def set_feedback(self, value):
        self.feedback = value

    def start(self):
        pass

    def stop(self):
        pass


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

    def set_competent (self, value):
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
