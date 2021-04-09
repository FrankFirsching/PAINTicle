# The painting logic for the particles

# <pep8 compliant>

from abc import ABC
from abc import abstractmethod

import bpy

from . import particles


class ParticlePainter(ABC):
    """ The abstract base class representing the painting logic for the
        particles. This can be different logics, like GPU based painting or
        utilizing blender's own painting logic through some weired hacks on
        the uv editor. """

    context = None

    def __init__(self, context: bpy.types.Context):
        self.context = context

    @abstractmethod
    def shutdown(self):
        """ Called before the containing particles object is destroyed. Can e.g. be used to unregister draw callbacks """
        pass

    @abstractmethod
    def draw(self, particles):
        pass

    def get_active_brush(self):
        """ Get the active brush """
        return self.context.tool_settings.image_paint.brush

    def get_active_image_slot(self):
        """ Return the active image slot for detecting changes in the painted image """
        return self.context.object.active_material.paint_active_slot

    def get_active_image(self):
        """ Get the texture we're painting to """
        image_slot = self.get_active_image_slot()
        paint_images = self.context.object.active_material.texture_paint_images
        return paint_images[image_slot] if image_slot<len(paint_images) else None

    def get_particle_settings(self):
        return self.context.scene.painticle_settings
