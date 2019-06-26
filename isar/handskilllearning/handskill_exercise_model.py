"""
Defining the exercises: FollowThePath
"""


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


class FollowThePathExercise(HandSkillExercise):
    def __init__(self):
        super().__init__()
        self.error = Error()
        self.time = Time()

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

    def set_feedback(self, value):
        self.feedback = value


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
