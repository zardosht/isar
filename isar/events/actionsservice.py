import logging
import traceback

from isar.events import actions
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
            logger.error("Action is None. Return")
            return

        if action.__class__.__name__ not in actions.global_action_types:
            if action.scene_id != self.current_scene.name:
                logger.error("action.scene_id is not the same as self.current_scene.name. Return.")
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
        self.current_scene = self.__scenes_model.get_current_scene()
        available_actions.extend(self.current_scene.get_actions())
        available_actions.extend(global_actions)
        return available_actions

    def get_action_by_name(self, name):
        available_actions = self.get_available_actions()
        for action in available_actions:
            if action.name == name:
                return action

    def set_current_scene(self, current_scene):
        self.current_scene = current_scene

    def start(self):
        pass

    def stop(self):
        pass


def init_global_actions():
    for action_class_name, action_type in global_action_types.items():
        action = action_type()
        action.name = action_type.global_action_name
        global_actions.append(action)


init_global_actions()


