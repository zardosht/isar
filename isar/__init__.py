from enum import Enum


class ApplicationMode(Enum):
    AUTHORING = 0
    EXECUTION = 1


application_mode = ApplicationMode.AUTHORING

CAMERA_UPDATE_INTERVAL = 100     # it is QTimer timeout interval in ms
OBJECT_DETECTION_INTERVAL = 100    # it is QTimer timeout interval in ms
SELECTION_STICK_TRACKING_INTERVAL = 0.1    # it is time.sleep() in sec




