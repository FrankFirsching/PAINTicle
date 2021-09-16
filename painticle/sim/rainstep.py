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

from ..interaction import Interactions
from . import emitterstep
from . import simulationstep

import mathutils


class RainStep(emitterstep.EmitterStep):

    def simulate(self, sim_data: simulationstep.SimulationData, particles: simulationstep.ParticleData,
                 forces: simulationstep.Forces, new_particles: simulationstep.ParticleData) -> simulationstep.Forces:
        input = sim_data.source_input
        if input.interactions & Interactions.EMIT_PARTICLES and input.pressure > 0.0:
            bbox_min, bbox_size = self.rearrange_bbox(sim_data.paint_mesh.object.bound_box)
            delta_t = sim_data.timestep
            time_between_particles = 1/(self.creation_settings.flow_rate * input.pressure)
            self.last_shoot_time += delta_t
            num_particles_to_shoot = int(self.last_shoot_time / time_between_particles)
            ray_origins, ray_directions = self.create_ray_data(num_particles_to_shoot, bbox_min, bbox_size, input)
            self.create_particles(ray_origins, ray_directions, sim_data, new_particles)
            self.last_shoot_time -= num_particles_to_shoot*time_between_particles
        return forces

    def create_ray_data(self, num_rays, bbox_min, bbox_size, source_input: simulationstep.SourceInput):
        ray_origins = []
        ray_directions = []
        for _ in range(num_rays):
            offset_x = bbox_min.x + bbox_size.x * self.rnd.random()
            offset_y = bbox_min.y + bbox_size.y * self.rnd.random()
            ray_origin = mathutils.Vector((offset_x, offset_y, bbox_min.z+bbox_size.z+1))
            ray_direction = mathutils.Vector(mathutils.Vector((0, 0, -1)))
            ray_origins.append(ray_origin)
            ray_directions.append(ray_direction)
        return ray_origins, ray_directions

    def rearrange_bbox(self, bbox):
        min = mathutils.Vector(bbox[0])
        max = mathutils.Vector(bbox[6])
        return min, (max-min)
