# This file is part of PAINTicle.
#
# PAINTicle is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAINTicle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PAINTicle.  If not, see <http://www.gnu.org/licenses/>.

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
