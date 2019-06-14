"""
Defining the exercises: FollowThePath, CatchTheObject
"""


# TODO: refactor the getter and setter of all classes

class HandSkillExercise:
    def __init__(self):
        self.scene = None
        self.feedback = FeedbackExercise()

    def get_scene(self):
        return self.scene

    def set_scene(self, value):
        self.scene = value


class FollowThePathExercise(HandSkillExercise):
    def __init__(self):
        super().__init__()
        self.error = Error()
        self.time = Time()

    def get_error(self):
        return self.error

    def get_time(self):
        return self.time
"""
Defining the feedback for the exercise
"""


class FeedbackExercise:
    def __init__(self):
        self.value_beginner = 0
        self.value_intermediate = 0
        self.value_competent = 0
        self.good = (0, 0)
        self.average = (0, 0)
        self.bad = (0, 0)

    def get_evaluation_list(self):
        return self.evaluationAspectList

    def add_to_evaluation_list(self, value):
        if isinstance(value, EvaluationAspect):
            self.evaluationAspectList.append(value)
            return True
        else:
            return False

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
        self._value = None
        self._value_weighted_combination = None

    def get_value(self):
        return self._value

    def set_value(self, value):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")

    def get_value_weighted_combination(self):
        return self._value_weighted_combination

    def set_value_weighted_combination(self, value):
        # It is important that the subclass sets its value.
        raise TypeError("Must be implemented by subclasses")


class Beginner(SkillLevel):
    def __init__(self):
        super().__init__()

    def set_value(self, value):
        self._value = value

    def set_value_weighted_combination(self, value):
        self._value_weighted_combination = value


class Intermediate(SkillLevel):
    def __init__(self):
        super().__init__()

    def set_value(self, value):
        self._value = value

    def set_value_weighted_combination(self, value):
        self._value_weighted_combination = value


class Competent(SkillLevel):
    def __init__(self):
        super().__init__()

    def set_value(self, value):
        self._value = value

    def set_value_weighted_combination(self, value):
        self._value_weighted_combination = value
