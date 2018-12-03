from isar.scene.scenemodel import Scene, ScenesModel

dummy_scene_model = None


def create_dummy_scenes_model():
    global dummy_scene_model
    dummy_scene_model = ScenesModel()
    return dummy_scene_model

