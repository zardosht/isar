import logging
import traceback

from isar.scene import audioutil
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


def get_action_by_name(name):
    for action in defined_actions:
        if action.name == name:
            return action


class ActionsService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.__annotations_model = None
        self.__scenes_model = None

        # TODO: Just for testing now. The actions are defined inside a project
        #  and must be loaded when project is loaded.
        #  Also, some of the actions are bound to a scene and must be only available on that scene,
        #  for example ShowAnnotations
        # self.init_defined_actions()

    def set_annotations_model(self, annotations_model):
        self.__annotations_model = annotations_model

    def set_scenes_model(self, scenes_model):
        self.__scenes_model = scenes_model

    def perform_action(self, action):
        if action is None:
            logger.warning("Action is None.")
            return

        if action.annotations_model is None:
            action.annotations_model = self.__annotations_model

        if action.scenes_model is None:
            action.scenes_model = self.__scenes_model

        try:
            action.run()
        except Exception as exp:
            logger.error("Exception thrown on performing the action: {}".format(str(action)))
            logger.error(exp)
            traceback.print_tb(exp.__traceback__)

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

    def find_annotations(self, annotation_names):
        if annotation_names is None:
            logger.error("annotation_names is none!")
            return []

        if self.annotations_model is None:
            logger.error("AnnotationsModel is none!")
            return []

        annotations = []
        for annotation_name in annotation_names:
            annotation = self.annotations_model.get_annotation_by_name(annotation_name)
            if annotation is None:
                logger.error("Could not find an annotation with name: {}".format(annotation_name))
                continue
            else:
                annotations.append(annotation)

        return annotations

    def find_annotation(self, annotation_name):
        if annotation_name is None:
            logger.error("annotation_name is none!")
            return None

        if self.annotations_model is None:
            logger.error("AnnotationsModel is none!")
            return None

        annotation = self.annotations_model.get_annotation_by_name(annotation_name)
        if annotation is None:
            logger.error("Could not find an annotation with name: {}".format(annotation_name))
        return annotation


class ToggleAnnotationVisibilityAction(Action):
    """
    Toggles the visibility of multiple annotations.

    """
    def __init__(self):
        super().__init__()
        self.annotation_names = None

    def run(self):
        annotations = self.find_annotations(self.annotation_names)
        for annotation in annotations:
            is_visible = annotation.show.get_value()
            annotation.show.set_value(not is_visible)


class ShowAnnotationAction(ToggleAnnotationVisibilityAction):
    def __init__(self):
        super().__init__()

    def run(self):
        annotations = self.find_annotations(self.annotation_names)
        for annotation in annotations:
            annotation.show.set_value(True)


class HideAnnotationAction(ToggleAnnotationVisibilityAction):
    def __init__(self):
        super().__init__()

    def run(self):
        annotations = self.find_annotations(self.annotation_names)
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


class StartTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    def __init__(self):
        super().__init__()
        self.timer_name = None

    def run(self):
        timer = self.find_annotation(self.timer_name)
        if timer is not None:
            timer.start()


class StopTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    def __init__(self):
        super().__init__()
        self.timer_name = None

    def run(self):
        timer = self.find_annotation(self.timer_name)
        if timer is not None:
            timer.stop()


class ResetTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    def __init__(self):
        super().__init__()
        self.timer_name = None

    def run(self):
        timer = self.find_annotation(self.timer_name)
        if timer is not None:
            timer.reset()


class PlaySoundAction(Action):
    """
    Must have a sound annotation as its target.
    """
    def __init__(self):
        super().__init__()
        self.annotation_name = None

    def run(self):
        annotation = self.find_annotation(self.annotation_name)
        if annotation is None:
            logger.error("Target annotation is None")
            return

        audio_file_path = annotation.audio_path.get_value()
        loop = annotation.loop_playback.get_value()
        audioutil.play(audio_file_path, loop)


class PlayVideoAction(Action):
    """
    Must have a video annotation as its target.
    """
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class StartAnimationAction(Action):
    def __init__(self):
        super().__init__()
        self.animation_name = None

    def run(self):
        animation = self.find_annotation(self.animation_name)
        animation.start()



# ====================================================
# ========= initializint defined actions   ===========
# ========= This must be read from project ===========
# ====================================================

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

    play_pincers_audio = PlaySoundAction()
    play_pincers_audio.name = "Play Pincers Audio"
    play_pincers_audio.annotation_name = "pincers_audio"
    defined_actions.append(play_pincers_audio)

    start_timer1 = StartTimerAction()
    start_timer1.name = "Start Timer 1"
    start_timer1.timer_name = "timer1"
    defined_actions.append(start_timer1)

    stop_timer1 = StopTimerAction()
    stop_timer1.name = "Stop Timer 1"
    stop_timer1.timer_name = "timer1"
    defined_actions.append(stop_timer1)

    reset_timer1 = ResetTimerAction()
    reset_timer1.name = "Reset Timer 1"
    reset_timer1.timer_name = "timer1"
    defined_actions.append(reset_timer1)

    start_fly_animation_1 = StartAnimationAction()
    start_fly_animation_1.name = "Start Fly Animation 1"
    start_fly_animation_1.animation_name = "fly_animation1"
    defined_actions.append(start_fly_animation_1)









