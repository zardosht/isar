import logging
import sys
import time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow

from isar.domainlearning.domainlearning import DomainLearningWindow, DomainLearningMainWindow
from isar.scene.definitionwindow import SceneDefinitionWindow
from isar.services import servicemanager


def configure_logging():
    # create logger with 'spam_application'
    logger = logging.getLogger('isar')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('isar.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info('Logging is configured.')


def main():
    # See: https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr
    # os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

    configure_logging()
    logger = logging.getLogger("isar")

    app = QtWidgets.QApplication(sys.argv)

    servicemanager.start_services()

    scene_defintion = True
    scene_defintion = False
    if scene_defintion:
        scene_def_window = QMainWindow(None)
        scene_def_window.setCentralWidget(SceneDefinitionWindow())
        scene_def_window.show()
    else:
        domain_learning_window = DomainLearningMainWindow()
        domain_learning_window.setCentralWidget(DomainLearningWindow(screen_id=2))
        domain_learning_window.move(100, 100)
        domain_learning_window.show()

    app.exec()

    time.sleep(0.5)
    servicemanager.stop_services()


if __name__ == "__main__":
    main()

