import logging


logger = logging.getLogger("isar.actionmanager")


defined_actions = []
annotations_model = None


def init_defined_actions():
    # TODO: This will be read from the prorject. During the scene definition, the user defines actions.
    #  They are persisted with project.
    toggle_red_box = ToggleAnnotationVisibilityAction()
    toggle_red_box.name = "Toggle Red Box"
    toggle_red_box.annotation_names = ["red_box"]
    defined_actions.append(toggle_red_box)

    toggle_help = ToggleAnnotationVisibilityAction()
    toggle_help.name = "Toggle Help"
    toggle_help.annotation_names = ["help_text1", "help_text2"]
    defined_actions.append(toggle_help)


def perform_action(action):
    if action is None:
        logger.warning("Action is None.")
        return

    action.run()


class Action():
    def __init__(self):
        self.name = "action"

    def run(self):
        # must be implemented by subclasses
        pass


class ToggleAnnotationVisibilityAction(Action):
    def __init__(self):
        super().__init__()
        self.annotation_names = None

    def run(self):
        if self.annotation_names is None:
            logger.error("annotation_name is none!")
            return

        if annotations_model is None:
            logger.error("AnnotationsModel is none!")
            return

        annotations = []
        for annotation_name in self.annotation_names:
            annotation = annotations_model.get_annotation_by_name(annotation_name)
            if annotation is None:
                logger.error("Could not find an annotation with name: {}".format(annotation_name))
                continue
            else:
                annotations.append(annotation)

        for annotation in annotations:
            is_visible = annotation.show.get_value()
            annotation.show.set_value(not is_visible)








