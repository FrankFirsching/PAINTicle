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
        self.barycentric = paint_mesh.barycentrics(self.location, self.tri_index)

        mesh = paint_mesh.mesh
        tri = mesh.loop_triangles[self.tri_index]
        n = [mathutils.Vector(n) for n in tri.split_normals]

        uvMap = mesh.uv_layers.active
        uv = [uvMap.data[i].uv.copy() for i in tri.loops]

        if all(coord > 0 for coord in self.barycentric):
            # If we're within the triangle...
            uv[0].resize_3d()
            uv[1].resize_3d()
            uv[2].resize_3d()
            uvx = paint_mesh.barycentrics(self.location, self.tri_index,
                                          uv[0], uv[1], uv[2])
            self.uv = uvx.resized(2)
            self.normal = paint_mesh.barycentrics(self.location, self.tri_index,
                                                  n[0], n[1], n[2])
            self.normal.normalize()

    def project_back_to_triangle(self, paint_mesh):
        # Put the particle back to the triangle surface
        if True:  # Use triangle neighbor info movement
            new_location = \
                paint_mesh.project_point_to_triangle(self.location, self.tri_index)
            new_location, new_tri_index, was_moved = \
                paint_mesh.move_over_triangle_boundaries(self.location, new_location, self.tri_index)
            if not was_moved:
                # If particle moved over boundary, let it die
                self.age = self.max_age+1
            self.location = new_location
            self.tri_index = new_tri_index
        else:
            result, location, normal, index = paint_mesh.object.closest_point_on_mesh(self.location)
            if result:
                self.location = location
                self.tri_index = paint_mesh.triangle_for_point_on_poly(location, index)
