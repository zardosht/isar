from isar.scene import util
from isar.scene.physicalobjectmodel import PhysicalObject


def draw_physical_object(opencv_img, phys_obj: PhysicalObject):
    height, width, _ = phys_obj.image.shape
    rel_x, rel_y = phys_obj.scene_position
    x, y = util.relative_coordinates_to_image_coordinates(opencv_img.shape, rel_x, rel_y)
    opencv_img[y:y + height, x:x + width] = phys_obj.image
