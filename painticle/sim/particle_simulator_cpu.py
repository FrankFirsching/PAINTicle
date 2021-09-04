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
from .. import utils
from .. import numpyutils
from .. import accel
from . import gravitystep, repelstep, dragstep, frictionstep
import bpy
import numpy as np


from painticle import trianglemesh
from ..numpyutils import float32_dtype, vec2_dtype, vec3_dtype, col_dtype

# This type needs to be conform to the definition of ParticleData in accel/particledata.h
particle_dtype = np.dtype([('location', vec3_dtype),
                           ('acceleration', vec3_dtype),
                           ('speed', vec3_dtype),
                           ('normal', vec3_dtype),
                           ('uv', vec2_dtype),
                           ('size', float32_dtype),
                           ('mass', float32_dtype),
                           ('age', float32_dtype),
                           ('max_age', float32_dtype),
                           ('color', col_dtype)],
                          align=True)


class ParticleSimulatorCPU(particle_simulator.ParticleSimulator):
    """ This particle simulator is using the CPU to simulate the particles. """

    def __init__(self, context: bpy.types.Context):
        super().__init__(context)
        self._particles = accel.ParticleData()
        self._physics_steps = [
            gravitystep.GravityStep(),
            repelstep.RepelStep(),
            dragstep.DragStep(),
            frictionstep.FrictionStep()
            ]
        self.hashed_grid = accel.HashedGrid(0.001)
        self._new_particles = None

    def shutdown(self):
        pass

    def add_particles(self, particles):
        self._particles.append(particles)

    @property
    def num_particles(self):
        return self._particles.num_particles

    def set_num_particles(self, num_particles):
        self._particles.resize(num_particles)

    def set_particle(self, i, particle):
        self._particles[i] = particle

    def clear_particles(self):
        self._particles.resize(0)

    def simulate(self, sim_data: particle_simulator.SimulationData):
        if self.num_particles > 0:
            # Data initialization
            # -------------------
            p = self._particles
            forces = np.zeros((self.num_particles, 3), float32_dtype)
            new_particles = accel.ParticleData()
            sim_data.hashed_grid = self.hashed_grid
            # Apply simulation steps
            # ----------------------
            for step in self._physics_steps:
                forces = step.simulate(sim_data, p, forces, new_particles)
            num_substeps = sim_data.settings.physics.sim_sub_steps
            for _ in range(num_substeps):
                # Improved Euler (midpoint) integration step
                # ------------------------------------------
                ulocation = numpyutils.unstructured(p.location)
                uspeed = numpyutils.unstructured(p.speed)
                uacceleration = numpyutils.unstructured(p.acceleration)
                new_acceleration = forces / p.mass[:, np.newaxis]
                half_timestep = 0.5 * sim_data.timestep / num_substeps
                new_speed = uspeed + half_timestep * (uacceleration + new_acceleration)
                new_location = ulocation + half_timestep * (uspeed + new_speed)
                p.acceleration = numpyutils.to_structured(new_acceleration, vec3_dtype)
                p.speed = numpyutils.to_structured(new_speed, vec3_dtype)
                p.location = numpyutils.to_structured(new_location, vec3_dtype)
            # Last step assign the new computed values
            p.age += sim_data.timestep
            self._particles.del_dead()
        if(self._new_particles is not None):
            self._particles.append(self._new_particles)
            self._new_particles = None
        self._update_location_dependent_variables(sim_data.paint_mesh)
        settings = sim_data.settings
        age_size_factor = max(1, settings.particle_size_age_factor)
        self.hashed_grid.voxel_size = (settings.particle_size + settings.particle_size_random) * age_size_factor
        self.hashed_grid.build(numpyutils.unstructured(self._particles.location))

    def _update_location_dependent_variables(self, paint_mesh: trianglemesh.TriangleMesh):
        result = paint_mesh.bvh.closest_points(self._particles.location)
        self._particles.location = result['location']
        self._particles.normal = result['normal']
        projected_speed = numpyutils.project_vector_onto_plane(self._particles.speed, self._particles.normal)
        self._particles.speed = numpyutils.to_structured(projected_speed, numpyutils.vec3_dtype)

    def create_uninitialized_particles(self, num_particles):
        particles = accel.ParticleData()
        particles.resize(num_particles)
        return particles

    def add_particles_from_rays(self, ray_origins, ray_directions, bvh, object_transform, brush_color,
                                painticle_settings):
        """ ray_origins and ray_directions need to be given in world space """
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
        if self._new_particles is None:
            self._new_particles = accel.ParticleData()
        self._new_particles.add_particles_from_rays(ray_origins, ray_directions, matrix_inv, bvh,
                                                    [speed, speed], [speed_random, speed_random, speed_random],
                                                    [size_min, size_max], [mass_min, mass_max],
                                                    [max_age_min, max_age_max],
                                                    brush_color[:], painticle_settings.color_random.hsv)
