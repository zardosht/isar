import logging
import traceback

from isar.events.actions import ToggleAnnotationVisibilityAction, ShowAnnotationAction, HideAnnotationAction, \
    ShowSceneAction, StartAudioAction, StartTimerAction, \
    StopTimerAction, ResetTimerAction, StartAnimationAction, StopAnimationAction, ParallelCompositeAction, \
    SequentialCompositeAction, global_action_types
from isar.services.service import Service


logger = logging.getLogger("isar.actionsservice")

"""
All the actions related to annotations, sound, video, timer, ... relate to the current scene. 
Only scene actions (show scene, next scene, previous scene) deal with another scene. 

The names of the annotations are unique inside the scene. 


------------ nonesense... because the __scene attribute of the annotations_model is automatically changed ---------

The annotations_model of the ActionsService (generally, whereever there is an annotations_model) should be updated
when scene is changed to another scene. (We probably need a SceneChangedEvent)
-------------------------------------------------------------------------------------------------------------------
"""


defined_actions = []
global_actions = []


class ActionsService(Service):
    def __init__(self, service_name):
        super().__init__(service_name)
        self.__annotations_model = None
        self.__scenes_model = None
        self.current_scene = None

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

        if action._action_service is None:
            action._action_service = self

        try:
            action.run()
        except Exception as exp:
            logger.error("Exception thrown on performing the action: {}".format(str(action)))
            logger.error(exp)
            traceback.print_tb(exp.__traceback__)

    def get_available_actions(self):
        available_actions = []
        # ---------------------------
        # self.current_scene = self.__scenes_model.get_current_scene()
        # available_actions.extend(self.current_scene.get_actions())
        # ---------------------------

        available_actions.extend(defined_actions)

        # ---------------------------

        available_actions.extend(global_actions)
        return available_actions

    def get_action_by_name(self, name):
        available_actions = self.get_available_actions()
        for action in available_actions:
            if action.name == name:
                return action

    def start(self):
        pass

    def stop(self):
        pass


# ====================================================
# ========= initializint defined actions   ===========
# ========= This must be read from project ===========
# ====================================================


def init_defined_actions():
    # TODO: This will be read from the prorject. During the scene definition, the user defines actions.
    #  They are persisted with project.

    global defined_actions
    defined_actions.clear()

    init_global_actions()

    annotation_names = ["red_box"]
    toggle_red_box = ToggleAnnotationVisibilityAction(annotation_names)
    toggle_red_box.name = "Toggle Red Box"
    defined_actions.append(toggle_red_box)

    annotation_names = ["red_circle"]
    toggle_red_circle = ToggleAnnotationVisibilityAction(annotation_names)
    toggle_red_circle.name = "Toggle Red Circle"
    defined_actions.append(toggle_red_circle)

    annotation_names = ["help_text1", "help_text2"]
    toggle_help = ToggleAnnotationVisibilityAction(annotation_names)
    toggle_help.name = "Toggle Help"
    defined_actions.append(toggle_help)

    annotation_names = ["lenna"]
    show_lenna = ShowAnnotationAction(annotation_names)
    show_lenna.name = "Show Lenna"
    defined_actions.append(show_lenna)

    annotation_names = ["lenna"]
    hide_lenna = HideAnnotationAction(annotation_names)
    hide_lenna.name = "Hide Lenna"
    defined_actions.append(hide_lenna)

    scene_name = "Scene1"
    show_scene1 = ShowSceneAction(scene_name)
    show_scene1.name = "Show Scene1"
    defined_actions.append(show_scene1)

    scene_name = "help"
    show_help_scene = ShowSceneAction(scene_name)
    show_help_scene.name = "Show Help Scene"
    defined_actions.append(show_help_scene)

    scene_name = "joke"
    show_joke_scene = ShowSceneAction(scene_name)
    show_joke_scene.name = "Show Joke Scene"
    defined_actions.append(show_joke_scene)

    annotation_name = "pincers_audio"
    play_pincers_audio = StartAudioAction(annotation_name)
    play_pincers_audio.name = "Play Pincers Audio"
    defined_actions.append(play_pincers_audio)

    timer_name = "timer1"
    start_timer1 = StartTimerAction(timer_name)
    start_timer1.name = "Start Timer 1"
    defined_actions.append(start_timer1)

    timer_name = "timer1"
    stop_timer1 = StopTimerAction(timer_name)
    stop_timer1.name = "Stop Timer 1"
    defined_actions.append(stop_timer1)

    timer_name = "timer1"
    reset_timer1 = ResetTimerAction(timer_name)
    reset_timer1.name = "Reset Timer 1"
    defined_actions.append(reset_timer1)

    animation_names = ["fly_animation1", "fly_animation2"]
    start_fly_animation_1 = StartAnimationAction(animation_names)
    start_fly_animation_1.name = "Start Fly Animation 1"
    defined_actions.append(start_fly_animation_1)

    animation_names = ["fly_animation1", "fly_animation2"]
    stop_fly_animation_1 = StopAnimationAction(animation_names)
    stop_fly_animation_1.name = "Stop Fly Animation 1"
    defined_actions.append(stop_fly_animation_1)

    start_timer1_and_play_pincers_audio = ParallelCompositeAction()
    start_timer1_and_play_pincers_audio.name = "Start Timer 1 AND Play Pincers Audio"
    start_timer1_and_play_pincers_audio.actions = [start_timer1, play_pincers_audio]
    defined_actions.append(start_timer1_and_play_pincers_audio)

    hide_lenna_then_show_lenna = SequentialCompositeAction()
    hide_lenna_then_show_lenna.name = "Hide lenna THEN Show lenna"
    hide_lenna_then_show_lenna.actions = [hide_lenna, show_lenna]
    defined_actions.append(hide_lenna_then_show_lenna)

    hide_lenna_then_show_lenna_then_toggle_redcircle = SequentialCompositeAction()
    hide_lenna_then_show_lenna_then_toggle_redcircle.name = "hide_lenna_then_show_lenna_then_toggle_redcircle"
    hide_lenna_then_show_lenna_then_toggle_redcircle.actions = [hide_lenna, show_lenna, toggle_red_circle]
    defined_actions.append(hide_lenna_then_show_lenna_then_toggle_redcircle)


def init_global_actions():
    for action_class_name, action_type in global_action_types.items():
        action = action_type()
        action.name = action_type.global_action_name
        global_actions.append(action)


init_defined_actions()


