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

# <pep8 compliant>

# A class representing a single particle

import array
import random

import mathutils

from . import physics
from . import utils


class Particle:
    """  A single particle. """

    _next_particle_id = 0
    rnd = random.Random()

    """ A single particle """
    def __init__(self, location, tri_index, color, paint_mesh, particle_settings):
        self.id = Particle._next_particle_id
        Particle._next_particle_id += 1
        self.location = location
        self.tri_index = tri_index
        self.acceleration = mathutils.Vector((0, 0, 0))
        self.speed = mathutils.Vector((0, 0, 0))
        self.barycentric = mathutils.Vector((0, 0, 0))
        self.normal = mathutils.Vector((0, 0, 0))
        self.uv = mathutils.Vector((0, 0))

        rnd = Particle.rnd
        random_size = rnd.uniform(-particle_settings.particle_size_random,
                                  particle_settings.particle_size_random)
        self.particle_size = particle_settings.particle_size+random_size

        random_mass = rnd.uniform(-particle_settings.mass_random,
                                  particle_settings.mass_random)
        self.mass = particle_settings.mass + random_mass

        self.age = 0.0
        random_age = rnd.uniform(-particle_settings.max_age_random,
                                 particle_settings.max_age_random)
        self.max_age = particle_settings.max_age + random_age

        col_rand = particle_settings.color_random
        self.color = color.copy()
        self.color.h += rnd.uniform(-col_rand.h, col_rand.h)
        self.color.s += rnd.uniform(-col_rand.s, col_rand.s)
        self.color.v += rnd.uniform(-col_rand.v, col_rand.v)

        if paint_mesh is not None:
            self.update_location_dependent_properties(paint_mesh)

    def move(self, physics: physics.Physics, paint_mesh, delta_t: float):
        ortho_force = physics.gravity.dot(self.normal) * self.normal
        plane_force = physics.gravity - ortho_force
        friction_force = ortho_force * physics.friction_coefficient
        # gravity on place and friction
        applied_force = plane_force - friction_force
        # Improved Euler (midpoint) integration step
        new_acceleration = applied_force/self.mass
        new_speed = self.speed + 0.5 * delta_t * (self.acceleration + new_acceleration)
        new_location = self.location + 0.5 * delta_t * (self.speed + new_speed)
        self.acceleration = new_acceleration
        self.speed = new_speed
        self.location = new_location
        self.age += delta_t
        self.update_location_dependent_properties(paint_mesh)

    def update_location_dependent_properties(self, paint_mesh):
        self.project_back_to_triangle(paint_mesh)
        bary = paint_mesh.barycentrics(self.location, self.tri_index)
        self.barycentric = bary

        if bary[0] > 0 and bary[1] > 0 and bary[2] > 0:
            # If we're within the triangle...
            mesh = paint_mesh.mesh
            tri = mesh.loop_triangles[self.tri_index]
            uvMap = mesh.uv_layers.active.data
            # Fully unrolled uv interpolation, due to performance reasons
            self.uv = uvMap[tri.loops[0]].uv*bary[0] + uvMap[tri.loops[1]].uv*bary[1] + uvMap[tri.loops[2]].uv*bary[2]

    def project_back_to_triangle(self, paint_mesh):
        # Put the particle back to the triangle surface
        location, normal, tri_index, barycentrics = paint_mesh.bvh.closest_point(self.location)
        if location is not None:
            self.location = mathutils.Vector(location)
            self.normal = mathutils.Vector(normal)
            self.tri_index = tri_index
