import logging

from isar.services.service import Service

logger = logging.getLogger("isar.actionsservice")


defined_actions = []


class ActionsService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.annotations_model = None

    @staticmethod
    def init_defined_actions():
        # TODO: This will be read from the prorject. During the scene definition, the user defines actions.
        #  They are persisted with project.

        global defined_actions
        defined_actions.clear()

        toggle_red_box = ToggleAnnotationVisibilityAction()
        toggle_red_box.name = "Toggle Red Box"
        toggle_red_box.annotation_names = ["red_box"]
        defined_actions.append(toggle_red_box)

        toggle_help = ToggleAnnotationVisibilityAction()
        toggle_help.name = "Toggle Help"
        toggle_help.annotation_names = ["help_text1", "help_text2"]
        defined_actions.append(toggle_help)

        show_lenna = ShowAnnotationAction()
        show_lenna.name = "Show Lenna"
        show_lenna.annotation_names = ["lenna"]
        defined_actions.append(show_lenna)

        hide_lenna = HideAnnotationAction()
        hide_lenna.name = "Hide Lenna"
        hide_lenna.annotation_names = ["lenna"]
        defined_actions.append(hide_lenna)

    def perform_action(self, action):
        if action is None:
            logger.warning("Action is None.")
            return

        if action.annotations_model is None:
            action.annotations_model = self.annotations_model

        action.run()

    def start(self):
        pass

    def stop(self):
        pass


class Action:
    def __init__(self):
        self.name = "action"
        self.annotations_model = None

    def run(self):
        # must be implemented by subclasses
        pass


class ToggleAnnotationVisibilityAction(Action):
    """
    Toggles the visibility of multiple annotations.

    """
    def __init__(self):
        super().__init__()
        self.annotation_names = None

    def run(self):
        annotations = self.find_annotation()
        for annotation in annotations:
            is_visible = annotation.show.get_value()
            annotation.show.set_value(not is_visible)

    def find_annotation(self):
        if self.annotation_names is None:
            logger.error("annotation_name is none!")
            return []

        if self.annotations_model is None:
            logger.error("AnnotationsModel is none!")
            return []

        annotations = []
        for annotation_name in self.annotation_names:
            annotation = self.annotations_model.get_annotation_by_name(annotation_name)
            if annotation is None:
                logger.error("Could not find an annotation with name: {}".format(annotation_name))
                continue
            else:
                annotations.append(annotation)

        return annotations


class ShowAnnotationAction(ToggleAnnotationVisibilityAction):
    def __init__(self):
        super().__init__()

    def run(self):
        annotations = self.find_annotation()
        for annotation in annotations:
            annotation.show.set_value(True)


class HideAnnotationAction(ToggleAnnotationVisibilityAction):
    def __init__(self):
        super().__init__()

    def run(self):
        annotations = self.find_annotation()
        for annotation in annotations:
            annotation.show.set_value(False)


class ShowSceneAction(Action):
    """
    Must have a scene as its target
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class NextSceneAction(Action):
    """
    Next scene in scene navigation sequence
    TODO: We need a scene service that keeps track of scene navigation.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class PreviousSceneAction(Action):
    """
    Previous scene in scene navigation sequence
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class PlaySoundAction(Action):
    """
    Must have a sound annotation as its target.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class PlayVideoAction(Action):
    """
    Must have a video annotation as its target.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class StartTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class PauseTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class ResetTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass





