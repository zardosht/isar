import logging
import sys
import time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from isar.services import servicemanager
from isar.scene.definitionwindow import SceneDefinitionWindow


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
    configure_logging()

    app = QtWidgets.QApplication(sys.argv)
    servicemanager.start_services()

    scene_def_window : QDialog = SceneDefinitionWindow()
    scene_def_window.exec()
    # app.exec()

    time.sleep(0.5)

    servicemanager.stop_services()


if __name__ == "__main__":
    main()

