import logging

from isar.services.service import Service

logger = logging.getLogger("isar.actionsservice")


defined_actions = []

"""
All the actions related to annotations, sound, video, timer, ... relate to the current scene. 
Only scene actions (show scene, next scene, previous scene) deal with another scene. 

The names of the annotations are unique inside the scene. 

------------ nonesense... because the __scene attribute of the annotations_model is automatically changed ---------

The annotations_model of the ActionsService (generally, whereever there is an annotations_model) should be updated
when scene is changed to another scene. (We probably need a SceneChangedEvent)
-------------------------------------------------------------------------------------------------------------------


"""


class ActionsService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.__annotations_model = None
        self.__scenes_model = None

        # TODO: Just for testing now. The actions are defined inside a project and must be loaded when project is loaded.
        #  Also, some of the actions are bound to a scene and must be only evailable on that scene,
        #  for example ShowAnnotations
        # self.init_defined_actions()

    def set_annotations_model(self, annotations_model):
        self.__annotations_model = annotations_model

    def set_scenes_model(self, scenes_model):
        self.__scenes_model = scenes_model

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

        show_scene1 = ShowSceneAction()
        show_scene1.name = "Show Scene1"
        show_scene1.scene_name = "Scene1"
        defined_actions.append(show_scene1)

        show_help_scene = ShowSceneAction()
        show_help_scene.name = "Show Help Scene"
        show_help_scene.scene_name = "help"
        defined_actions.append(show_help_scene)

        show_joke_scene = ShowSceneAction()
        show_joke_scene.name = "Show Joke Scene"
        show_joke_scene.scene_name = "joke"
        defined_actions.append(show_joke_scene)

        next_scene = NextSceneAction()
        next_scene.name = "Next Scene"
        defined_actions.append(next_scene)

        prev_scene = PreviousSceneAction()
        prev_scene.name = "Previous Scene"
        defined_actions.append(prev_scene)

        back_scene = BackSceneAction()
        back_scene.name = "Back Scene"
        defined_actions.append(back_scene)

    def perform_action(self, action):
        if action is None:
            logger.warning("Action is None.")
            return

        if action.annotations_model is None:
            action.annotations_model = self.__annotations_model

        if action.scenes_model is None:
            action.scenes_model = self.__scenes_model

        action.run()

    def start(self):
        pass

    def stop(self):
        pass


class Action:
    def __init__(self):
        self.name = "action"
        self.annotations_model = None
        self.scenes_model = None

    def run(self):
        # must be implemented by subclasses
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["annotations_model"]
        del state["scenes_model"]
        return state

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)


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
        self.scene_name = None

    def run(self):
        self.scenes_model.show_scene(self.scene_name)


class NextSceneAction(Action):
    """
    Next scene in scene navigation sequence
    """
    def __init__(self):
        super().__init__()

    def run(self):
        self.scenes_model.show_next_scene()


class PreviousSceneAction(Action):
    """
    Previous scene in scene navigation sequence
    """
    def __init__(self):
        super().__init__()

    def run(self):
        self.scenes_model.show_previous_scene()


class BackSceneAction(Action):
    """
    Back scene. This is added for the cases where user views a scene that is not part of the
    defined navigation. Imagine for example a navigation flow consists of [S1, S2, S3]
    for S2 we have a scene H1 that shows help, and is shown using an action button. On the help scene (H1),
    an action button calls the back action to return to S2. This is different from previous scene action, that
    refers to the previous scene in navigation flow, i.e. S1
    """
    def __init__(self):
        super().__init__()

    def run(self):
        self.scenes_model.show_back_scene()


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





