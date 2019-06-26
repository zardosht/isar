"""
Defining the exercises: FollowThePath
"""
from isar.scene.annotationmodel import CurveAnnotation


class HandSkillExercise:
    def __init__(self):
        self.name = None
        self.scene = None
        self.feedback = Feedback()

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
        curve = self.scene.get_all_annotations_by_type(CurveAnnotation)
        curve[0].exercise = self

    def set_feedback(self, value):
        self.feedback = value

    def start(self):
        # TODO: start TimerAnnotation just one time
        self.running = True
        print("Start Exercise")

    # TODO: stop exercise if time is up and compute feedback

    def stop(self):
        # TODO: stop timer if finish reached
        self.running = False
        print("Stop Exercise")

        # TODO: give feedback
        print(self.register_points)
        actual = self.scene.get_all_annotations_by_type(CurveAnnotation)
        print(actual[0].line_points_distributed)
        captured_positions = correct_positions(actual[0].line_points_distributed, self.register_points)
        print(captured_positions)
        number_captured = len(captured_positions)
        print(number_captured)

        max_points_number = actual[0].points.get_value()

        if number_captured >= (self.feedback.get_good() * max_points_number)/100:
            print("FEEDBACK GOOD!!!!!!!!")
        elif number_captured >= (self.feedback.get_average() * max_points_number)/100:
            print("FEEDBACK AVERAGE!!!!!!!!")
        elif number_captured >= (self.feedback.get_good() * max_points_number)/100:
            print("FEEDBACK BAD!!!!!!!!")
        else:
            print("FEEDBACK NOT EXISTING")

    def some_where(self):
        # eventmanger.fire_my_fancy_exercise_event(event info)
        pass


""" 
Defining a method that returns all points which where captured 
by the user with the tool and are in the defined line positions
"""


def correct_positions(actual_positions, registered_positions):
    return [x for x in actual_positions if x in registered_positions]


"""
Defining the feedback for the exercise
"""


class Feedback:
    def __init__(self):
        self.good = None
        self.average = None
        self.bad = None

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
