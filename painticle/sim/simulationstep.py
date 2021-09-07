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


from abc import ABC
from abc import abstractmethod

from . import particle_simulator
from .. import accel, utils

import numpy as np


# Define some datatypes used in the simulation step locally
SimulationData = particle_simulator.SimulationData
SourceInput = particle_simulator.SourceInput
ParticleData = accel.ParticleData
Forces = np.array


class SimulationStep(ABC):
    @abstractmethod
    def simulate(self, sim_data: SimulationData, particles: ParticleData, forces: Forces,
                 new_particles: ParticleData) -> Forces:
        pass

    def create_particles(self, ray_origins, ray_directions, sim_data: SimulationData, new_particles: ParticleData):
        """ ray_origins and ray_directions need to be given in world space """
        object_transform = sim_data.paint_mesh.object.matrix_world.copy()
        painticle_settings = sim_data.settings
        brush_color = sim_data.context.tool_settings.image_paint.brush.color
        bvh = sim_data.paint_mesh.bvh
        matrix_inv = utils.matrix_to_tuple(object_transform.inverted())
        physics = painticle_settings.physics
        speed = physics.initial_speed
        speed_random = 0.5 * physics.initial_speed * physics.initial_speed_random
        size_min = painticle_settings.particle_size - painticle_settings.particle_size_random
        size_max = painticle_settings.particle_size + painticle_settings.particle_size_random
        mass_min = painticle_settings.mass - painticle_settings.mass_random
        mass_max = painticle_settings.mass + painticle_settings.mass_random
        max_age_min = painticle_settings.max_age - painticle_settings.max_age_random
        max_age_max = painticle_settings.max_age + painticle_settings.max_age_random
        new_particles.add_particles_from_rays(ray_origins, ray_directions, matrix_inv, bvh,
                                              [speed, speed], [speed_random, speed_random, speed_random],
                                              [size_min, size_max], [mass_min, mass_max],
                                              [max_age_min, max_age_max],
                                              brush_color[:], painticle_settings.color_random.hsv)
