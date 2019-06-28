import logging
import sys
import time

from PyQt5 import QtWidgets

import isar
from isar import ApplicationMode
from isar.domainlearning.domainlearning import DomainLearningWindow
from isar.handskilllearning.handskill_exercise_definition import HandSkillExerciseDefinition
from isar.handskilllearning.handskill_exercise_execution import HandSkillExerciseExecution
from isar.scene.definitionwindow import SceneDefinitionWindow
from isar.services import servicemanager


def configure_logging():
    # create logger with 'spam_application'
    logger = logging.getLogger('isar')
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('isar.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.info('Logging is configured.')


def main():
    # See: https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr
    # os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

    configure_logging()
    logger = logging.getLogger("isar")

    app = QtWidgets.QApplication(sys.argv)

    use_case = input(
        "1 - Scene Definition \n" +
        "2 - Domain Learning \n" +
        "3 - Hand skill Exercise Definition \n" +
        "4 - Hand skill Exercise Execution \n\n" +
        "Enter option [1, 2, 3, 4]: ")

    all_services_initialized = servicemanager.start_services()
    if not all_services_initialized:
        logger.error("Could not intialize services. Return.")
        return

    if use_case == "1":
        isar.application_mode = ApplicationMode.AUTHORING
        scene_def_window = SceneDefinitionWindow()
        scene_def_window.show()
        app.exec()

    elif use_case == "2":
        isar.application_mode = ApplicationMode.EXECUTION
        domain_learning_window = DomainLearningWindow(screen_id=2)
        if domain_learning_window.projector_initialized:
            domain_learning_window.move(100, 100)
            domain_learning_window.show()
            app.exec()

    elif use_case == "3":
        isar.application_mode = ApplicationMode.EXECUTION
        hand_skill_exercise_definition_window = HandSkillExerciseDefinition()
        hand_skill_exercise_definition_window.move(100, 100)
        hand_skill_exercise_definition_window.show()
        app.exec()

    elif use_case == "4":
        isar.application_mode = ApplicationMode.EXECUTION
        hand_skill_exercise_execution_window = HandSkillExerciseExecution(screen_id=1)
        if hand_skill_exercise_execution_window.projector_initialized:
            hand_skill_exercise_execution_window.move(100, 100)
            hand_skill_exercise_execution_window.show()
            app.exec()

    time.sleep(0.5)
    servicemanager.stop_services()


if __name__ == "__main__":
    main()
