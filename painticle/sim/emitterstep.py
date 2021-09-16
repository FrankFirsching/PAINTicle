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

# The particle painter, that's using the gpu directly

# <pep8 compliant>


from abc import abstractmethod

from bpy.types import PropertyGroup

from . import simulationstep
from . import particle_simulator
from .. import accel, utils
from ..settings.particlecreationsettings import ParticleCreationSettings

from bpy.props import PointerProperty
import numpy as np
import random


class EmitterStep(simulationstep.SimulationStep):

    creation_settings: PointerProperty(type=ParticleCreationSettings, name="Creation settings",
                                       options=set())

    def initialize(self):
        self.last_shoot_time = 0
        self.rnd = random.Random()

    def create_particles(self, ray_origins, ray_directions, sim_data: simulationstep.SimulationData,
                         new_particles: simulationstep.ParticleData):
        """ ray_origins and ray_directions need to be given in world space """
        object_transform = sim_data.paint_mesh.object.matrix_world.copy()
        emit_settings = self.creation_settings
        brush_color = sim_data.context.tool_settings.image_paint.brush.color
        bvh = sim_data.paint_mesh.bvh
        matrix_inv = utils.matrix_to_tuple(object_transform.inverted())
        speed = emit_settings.initial_speed
        speed_random = 0.5 * emit_settings.initial_speed * emit_settings.initial_speed_random
        size_min = emit_settings.particle_size - emit_settings.particle_size_random
        size_max = emit_settings.particle_size + emit_settings.particle_size_random
        mass_min = emit_settings.mass - emit_settings.mass_random
        mass_max = emit_settings.mass + emit_settings.mass_random
        max_age_min = emit_settings.max_age - emit_settings.max_age_random
        max_age_max = emit_settings.max_age + emit_settings.max_age_random
        new_particles.add_particles_from_rays(ray_origins, ray_directions, matrix_inv, bvh,
                                              [speed, speed], [speed_random, speed_random, speed_random],
                                              [size_min, size_max], [mass_min, mass_max],
                                              [max_age_min, max_age_max],
                                              brush_color[:], emit_settings.color_random.hsv)
