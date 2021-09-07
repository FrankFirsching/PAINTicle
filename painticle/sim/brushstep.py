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

from . import particle_simulator
from . import simulationstep

import bpy
import random
import math


class BrushStep(simulationstep.SimulationStep):
    def __init__(self):
        self.last_shoot_time = 0
        self.rnd = random.Random()

    def simulate(self, sim_data: simulationstep.SimulationData, particles: simulationstep.ParticleData,
                 forces: simulationstep.Forces, new_particles: simulationstep.ParticleData) -> simulationstep.Forces:
        input = sim_data.source_input
        if input.interactions & particle_simulator.Interactions.EMIT_PARTICLES and input.pressure > 0.0:
            painticle_settings = sim_data.settings
            context = sim_data.context
            delta_t = sim_data.timestep
            time_between_particles = 1/(painticle_settings.flow_rate * input.pressure)
            self.last_shoot_time += delta_t
            num_particles_to_shoot = int(self.last_shoot_time / time_between_particles)
            ray_origins, ray_directions = self.create_ray_data(num_particles_to_shoot, context, input)
            self.create_particles(ray_origins, ray_directions, sim_data, new_particles)
            self.last_shoot_time -= num_particles_to_shoot*time_between_particles
        return forces

    def create_ray_data(self, num_rays, context: bpy.types.Context, source_input: simulationstep.SourceInput):
        ray_origins = []
        ray_directions = []
        brush_size = source_input.size * source_input.pressure
        for _ in range(num_rays):
            angle = 2*math.pi*self.rnd.random()
            distance = brush_size*self.rnd.random()
            offset_x = math.cos(angle)*distance
            offset_y = math.sin(angle)*distance
            ray_origin, ray_direction = self.get_ray(offset_x, offset_y, source_input)
            ray_origins.append(ray_origin)
            ray_directions.append(ray_direction)
        return ray_origins, ray_directions

    def get_brush_size(self, context: bpy.types.Context):
        """ Get the active brush size """
        return context.tool_settings.unified_paint_settings.size

    def get_ray(self, offset_x, offset_y, source_input: simulationstep.SourceInput):
        """ Get the ray under the mouse cursor """
        ray_direction = (offset_x * source_input.frame.right +
                         offset_y * source_input.frame.up +
                         source_input.frame.direction)

        return source_input.frame.origin, ray_direction
