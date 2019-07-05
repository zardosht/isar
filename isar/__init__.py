from enum import Enum


class ApplicationMode(Enum):
    AUTHORING = 0
    EXECUTION = 1


application_mode = ApplicationMode.AUTHORING

POISON_PILL = "poison_pill"

CAMERA_UPDATE_INTERVAL = 50     # it is QTimer timeout interval in ms
OBJECT_DETECTION_INTERVAL = 0.1    # it is QTimer timeout interval in ms
SELECTION_STICK_TRACKING_INTERVAL = 0.05    # it is time.sleep() in sec




