import logging
import time
from threading import Thread

from isar.scene import audioutil
from isar.scene.scenemodel import Scene

logger = logging.getLogger("isar.events.actions")


class Action:
    # if an action has extra properties, it must set this to true,
    # and give an implementation for update_action_properties_frame(qt_frame)
    has_properties = False
    has_target = True
    has_single_target = False

    def __init__(self, target=None):
        self.name = "action"
        self.target = target
        self.annotations_model = None
        self.scenes_model = None
        self._action_service = None

    def run(self):
        # must be implemented by subclasses
        pass

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["annotations_model"]
        del state["scenes_model"]
        del state["_action_service"]
        return state

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)

    def find_annotations(self):
        if self.target is None:
            logger.error("target is none!")
            return []

        if self.annotations_model is None:
            logger.error("AnnotationsModel is none!")
            return []

        annotations = []
        if type(self.target) == list:
            for annotation_name in self.target:
                annotation = self.annotations_model.get_annotation_by_name(annotation_name)
                if annotation is None:
                    logger.error("Could not find an annotation with name: {}".format(annotation_name))
                    continue
                else:
                    annotations.append(annotation)

            return annotations
        else:
            return self.find_annotation(self.target)

    def find_annotation(self, target):
        if target is None:
            logger.error("annotation_name is none!")
            return None

        if self.annotations_model is None:
            logger.error("AnnotationsModel is none!")
            return None

        annotation = self.annotations_model.get_annotation_by_name(target)
        if annotation is None:
            logger.error("Could not find an annotation with name: {}".format(target))
        return annotation

    @classmethod
    def update_action_properties_frame(cls, qt_frame):
        pass


class ToggleAnnotationVisibilityAction(Action):
    """
    Toggles the visibility of multiple annotations.
    """
    from isar.scene.annotationmodel import Annotation
    target_types = [Annotation]

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        annotations = self.find_annotations()
        for annotation in annotations:
            is_visible = annotation.show.get_value()
            annotation.show.set_value(not is_visible)


class ShowAnnotationAction(ToggleAnnotationVisibilityAction):
    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        annotations = self.find_annotations()
        for annotation in annotations:
            annotation.show.set_value(True)


class HideAnnotationAction(ToggleAnnotationVisibilityAction):
    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        annotations = self.find_annotations()
        for annotation in annotations:
            annotation.show.set_value(False)


class ShowSceneAction(Action):
    """
    Must have a scene as its target
    """
    target_types = [Scene]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        if type(self.target) == str:
            self.scenes_model.show_scene(self.scene_name)
        else:
            logger.warning("scene name is invalid: {}", str(self.target))


class NextSceneAction(Action):
    """
    Next scene in scene navigation sequence
    """
    global_action_name = "Next Scene"
    has_target = False

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        self.scenes_model.show_next_scene()


class PreviousSceneAction(Action):
    """
    Previous scene in scene navigation sequence
    """
    global_action_name = "Previous Scene"
    has_target = False

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        self.scenes_model.show_previous_scene()


class BackSceneAction(Action):
    """
    Back scene. This is added for the cases where user views a scene that is not part of the
    defined navigation flow. Imagine for example a navigation flow consists of [S1, S2, S3]
    for S2 we have a scene H1 that shows help, and is shown using an action button. On the help scene (H1),
    an action button calls the back action to return to S2. This is different from previous scene action, that
    refers to the previous scene in navigation flow, i.e. S1
    """
    global_action_name = "Back Scene"
    has_target = False

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        self.scenes_model.show_back_scene()


class StartTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        timer = self.find_annotations()
        if timer is not None:
            timer.start()


class StopTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)
        self.timer_name = None

    def run(self):
        timer = self.find_annotations()
        if timer is not None:
            timer.stop()


class ResetTimerAction(Action):
    """
    Must have a timer annotation as its target.
    """
    from isar.scene.annotationmodel import TimerAnnotation
    target_types = [TimerAnnotation]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)
        self.timer_name = None

    def run(self):
        timer = self.find_annotations()
        if timer is not None:
            timer.reset()


class StartAudioAction(Action):
    """
    Must have a sound annotation as its target.
    """
    from isar.scene.annotationmodel import AudioAnnotation
    target_types = [AudioAnnotation]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)
        self.annotation_name = None

    def run(self):
        annotation = self.find_annotations()
        if annotation is None:
            logger.error("Target annotation is None")
            return

        audio_file_path = annotation.audio_path.get_value()
        loop = annotation.loop_playback.get_value()
        audioutil.play(audio_file_path, loop)


class StopAudioAction(Action):
    """
    Must have a sound annotation as its target.
    """
    from isar.scene.annotationmodel import AudioAnnotation
    target_types = [AudioAnnotation]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)
        self.annotation_name = None

    def run(self):
        annotation = self.find_annotations()
        if annotation is None:
            logger.error("Target annotation is None")
            return

        audio_file_path = annotation.audio_path.get_value()
        audioutil.stop(audio_file_path)


class StartVideoAction(Action):
    """
    Must have a video annotation as its target.
    """
    from isar.scene.annotationmodel import VideoAnnotation
    target_types = [VideoAnnotation]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        # TODO: not implemented
        pass


class StopVideoAction(Action):
    """
    Must have a video annotation as its target.
    """
    from isar.scene.annotationmodel import VideoAnnotation
    target_types = [VideoAnnotation]
    has_single_target = True

    def __init__(self, target=None):
        super().__init__(target)

    def run(self):
        # TODO: not implemented
        pass


class StartAnimationAction(Action):
    from isar.scene.annotationmodel import AnimationAnnotation
    target_types = [AnimationAnnotation]

    def __init__(self, target=None):
        super().__init__(target)
        self.animation_names = None

    def run(self):
        animations = self.find_annotations()
        if animations is not None and len(animations) != 0:
            for animation in animations:
                animation.start()


class StopAnimationAction(Action):
    from isar.scene.annotationmodel import AnimationAnnotation
    target_types = [AnimationAnnotation]

    def __init__(self, target=None):
        super().__init__(target)
        self.animation_names = None

    def run(self):
        animations = self.find_annotations()
        if animations is not None and len(animations) != 0:
            for animation in animations:
                animation.stop()


class ParallelCompositeAction(Action):
    has_target = False
    has_properties = True

    def __init__(self, target=None):
        super().__init__(target)
        self.actions = []

    def run(self):
        for action in self.actions:
            t = Thread(target=lambda a: self._action_service.perform_action(a), args=(action, ))
            t.start()

    @classmethod
    def update_action_properties_frame(cls, qt_frame):
        # TODO:
        pass


class SequentialCompositeAction(Action):
    has_target = False
    has_properties = True

    def __init__(self, target=None):
        super().__init__(target)
        self.actions = []
        self.time_between_actions = 1

    def run(self):
        t = Thread(target=self.do_run)
        t.start()

    def do_run(self):
        for action in self.actions:
            self._action_service.perform_action(action)
            time.sleep(self.time_between_actions)

    @classmethod
    def update_action_properties_frame(cls, qt_frame):
        # TODO:
        pass


scene_action_types = {
    ToggleAnnotationVisibilityAction.__name__: ToggleAnnotationVisibilityAction,
    ShowAnnotationAction.__name__: ShowAnnotationAction,
    HideAnnotationAction.__name__: HideAnnotationAction,
    ShowSceneAction.__name__: ShowSceneAction,
    StartTimerAction.__name__: StartTimerAction,
    StopTimerAction.__name__: StopTimerAction,
    ResetTimerAction.__name__: ResetTimerAction,
    StartAudioAction.__name__: StartAudioAction,
    StopAudioAction.__name__: StopAudioAction,
    StartVideoAction.__name__: StartVideoAction,
    StopVideoAction.__name__: StopVideoAction,
    StartAnimationAction.__name__: StartAnimationAction,
    StopAnimationAction.__name__: StopAnimationAction,
    ParallelCompositeAction.__name__: ParallelCompositeAction,
    SequentialCompositeAction.__name__: SequentialCompositeAction
}


global_action_types = {
    NextSceneAction.__name__: NextSceneAction,
    PreviousSceneAction.__name__: PreviousSceneAction,
    BackSceneAction.__name__: BackSceneAction
}




