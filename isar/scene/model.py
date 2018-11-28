from isar.scene.scenemodel import Scene, ScenesModel

dummy_scene_model = None


def create_dummy_scenes_model():
    global dummy_scene_model
    scene1 = Scene("scene1")
    dummy_scene_model = ScenesModel()
    dummy_scene_model.scenes.append(scene1)
    return dummy_scene_model

