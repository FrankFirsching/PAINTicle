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
from painticle import trianglemesh

from . import particle_simulator
from . import numpyutils

import bpy
import mathutils
import numpy as np

import random
import time


float32_dtype = np.single
float64_dtype = np.double
vec2_dtype = np.dtype([('x', float32_dtype), ('y', float32_dtype)], align=True)
vec3_dtype = np.dtype([('x', float32_dtype), ('y', float32_dtype), ('z', float32_dtype)], align=True)
col_dtype = np.dtype([('r', float32_dtype), ('g', float32_dtype), ('b', float32_dtype)], align=True)
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


ParticleData = numpyutils.UnstructuredHolder


class SimulationStep(ABC):
    @abstractmethod
    def simulate(self, sim_data: particle_simulator.SimulationData, particles: ParticleData, forces, locations):
        pass


class GravityStep(SimulationStep):
    def simulate(self, sim_data: particle_simulator.SimulationData, particles: ParticleData, forces, locations):
        physics = sim_data.settings.physics
        gravity = physics.gravity
        # Calculation
        # Project gravity onto normal vector
        # We don't need to divide by the square length of normal, since this is a normalized vector.
        factor = particles.normal.dot(gravity)
        ortho_force = particles.normal * factor[:, np.newaxis]
        # The force on the plane is then just simple vector subtraction
        plane_force = np.array(gravity)[np.newaxis, :] - ortho_force
        # factor is the inverse of what we need here, since the normal is pointing to the outside of the surface,
        # but friction only applies if force is applied towards the surface. Hence we use (1+x) instead of (1-x)
        friction = np.clip(1+physics.friction_coefficient*factor/numpyutils.vec_length(plane_force), 0, 1)
        forces += plane_force * friction[:, np.newaxis]


class DragForce (SimulationStep):
    def simulate(self, sim_data: particle_simulator.SimulationData, particles: ParticleData, forces, locations):
        pass


class ParticleSimulatorCPU(particle_simulator.ParticleSimulator):
    """ This particle simulator is using the CPU to simulate the particles. """
    rnd = random.Random()

    def __init__(self, context: bpy.types.Context):
        super().__init__(context)
        self._particles = np.empty(0, dtype=particle_dtype)
        self._physics_steps = [GravityStep()]

    def shutdown(self):
        pass

    def add_particles(self, particles):
        self._particles = np.append(self._particles, particles)

    def set_num_particles(self, num_particles):
        self._particles.resize(num_particles, refcheck=False)

    def set_particle(self, i, particle):
        self._particles[i] = particle

    def clear_particles(self):
        self._particles = np.empty(0, dtype=particle_dtype)

    def simulate(self, sim_data: particle_simulator.SimulationData):
        # Data initialization
        # -------------------
        p = ParticleData(self._particles)
        forces = np.zeros((self._particles.size, 3), float32_dtype)
        locations = np.copy(p.location)
        # Apply simulation steps
        # ----------------------
        for step in self._physics_steps:
            step.simulate(sim_data, p, forces, locations)
        # Improved Euler (midpoint) integration step
        # ------------------------------------------
        new_acceleration = forces / p.mass[:,np.newaxis]
        half_timestep = 0.5 * sim_data.timestep
        new_speed = p.speed + half_timestep * (p.acceleration + new_acceleration)
        new_location = p.location + half_timestep * (p.speed + new_speed)
        # Last step assign the new computed values
        self._particles['acceleration'] = numpyutils.to_structured(new_acceleration, vec3_dtype)
        self._particles['speed'] = numpyutils.to_structured(new_speed, vec3_dtype)
        self._particles['location'] = numpyutils.to_structured(new_location, vec3_dtype)
        self._particles['age'] += sim_data.timestep
        self._update_location_dependent_variables(sim_data.paint_mesh)
        self.del_dead_particles()

    def _update_location_dependent_variables(self, paint_mesh: trianglemesh.TriangleMesh):
        loc = self._particles['location']
        result = paint_mesh.bvh.closest_points(numpyutils.unstructured(loc))
        self._particles['location'] = result['location']
        self._particles['normal'] = result['normal']

        barycentrics = numpyutils.unstructured(result['barycentrics'])
        tri_index = result['tri_index']
        active_uvs = paint_mesh.get_active_uvs()
        result_vertex_ids = np.take(paint_mesh.triangles, tri_index, axis=0)
        tri_uv = np.take(active_uvs, result_vertex_ids, axis=0)
        weighted_uvs = barycentrics[..., np.newaxis]*tri_uv
        self._particles['uv'] = numpyutils.to_structured(np.sum(weighted_uvs, axis=1), vec2_dtype)

    def del_dead_particles(self):
        alive_ones = self._particles['age'] <= self._particles['max_age']
        self._particles = self._particles[alive_ones, ...]

    @property
    def num_particles(self):
        return self._particles.size

    def create_particle(self, location, brush_color, speed, painticle_settings):
        p = np.zeros(1, particle_dtype)
        p['location'] = location
        p['speed'] = speed

        rnd = ParticleSimulatorCPU.rnd
        random_size = rnd.uniform(-painticle_settings.particle_size_random,
                                  painticle_settings.particle_size_random)
        p['size'] = painticle_settings.particle_size+random_size

        random_mass = rnd.uniform(-painticle_settings.mass_random,
                                  painticle_settings.mass_random)
        p['mass'] = painticle_settings.mass + random_mass

        p['age'] = 0.0
        random_age = rnd.uniform(-painticle_settings.max_age_random,
                                 painticle_settings.max_age_random)
        p['max_age'] = painticle_settings.max_age + random_age

        col_rand = painticle_settings.color_random
        color = mathutils.Color(brush_color)
        color.h += rnd.uniform(-col_rand.h, col_rand.h)
        color.s += rnd.uniform(-col_rand.s, col_rand.s)
        color.v += rnd.uniform(-col_rand.v, col_rand.v)
        p['color'] = (color.r, color.g, color.b)
        return p
