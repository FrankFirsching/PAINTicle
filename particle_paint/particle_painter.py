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
        return self.context.object.active_material.texture_paint_images[self.get_active_image_slot()]

    def get_particle_settings(self):
        return self.context.scene.particle_paint_settings
