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

# A particles shooter class

from painticle import particle_simulator
from bpy_extras import view3d_utils
import bpy
import mathutils

import array
import math
import random

from . import trianglemesh
from . import particle_simulator_cpu

from . import particle


class Particles:
    """ A class managing the particle system for the paint operator """
    def __init__(self, context: bpy.types.Context, omit_painter=False, use_simulator=True):
        """ If omit_painter is True, paint_particles and undo_last_paint may not be called. """
        from . import particle_painter_gpu
        self.rnd = random.Random()
        self.paint_mesh = trianglemesh.TriangleMesh(context)
        self.matrix = self.paint_mesh.object.matrix_world.copy()
        if use_simulator:
            self.simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
            self.particles = None
        else:
            self.simulator = None
            self.particles = []
        if omit_painter:
            self.painter = None
        else:
            self.painter = particle_painter_gpu.ParticlePainterGPU(context)        
        self.last_shoot_time = 0

    def __del__(self):
        if self.painter is not None:
            self.painter.shutdown()

    def numParticles(self):
        """ Return the number of simulated particles """
        if self.particles is not None:
            return len(self.particles)
        else:
            return self.simulator.num_particles

    def shoot(self, context: bpy.types.Context, event, delta_t, particle_settings):
        """ Shoot particles according to the flow rate """
        time_between_particles = 1/particle_settings.flow_rate
        self.last_shoot_time += delta_t
        num_particles_to_shoot = int(self.last_shoot_time / time_between_particles)
        if self.particles is not None:
            old_num_particles = len(self.particles)
            self.particles.extend([None]*num_particles_to_shoot)
        else:
            old_num_particles = self.simulator.num_particles
            self.simulator.set_num_particles(old_num_particles + num_particles_to_shoot)

        index = old_num_particles
        for i in range(num_particles_to_shoot):
            if self.shoot_single(index, context, event, particle_settings):
                index += 1
        
        if self.particles is not None:
            self.particles = self.particles[:index]
        else:
            self.simulator.set_num_particles(index)

        self.last_shoot_time -= num_particles_to_shoot*time_between_particles

    def shoot_single(self, index, context: bpy.types.Context, event, particle_settings):
        """ Shoot a single particle """
        paint_size = self.get_brush_size(context)
        angle = 2*math.pi*self.rnd.random()
        distance = paint_size*self.rnd.random()
        offset_x = math.cos(angle)*distance
        offset_y = math.sin(angle)*distance
        ray_origin, ray_direction = self.get_ray(context,
                                                event.mouse_x+offset_x,
                                                event.mouse_y+offset_y)
        location, normal, tri_index = self.ray_cast_on_object(ray_origin, ray_direction)
        if location is not None:
            ray_direction_unit = ray_direction.normalized()
            view_speed = particle_settings.physics.initial_speed * ray_direction_unit
            physics = particle_settings.physics
            max_initial_random = 0.5 * physics.initial_speed * physics.initial_speed_random
            view_speed += mathutils.Vector((random.uniform(-max_initial_random, max_initial_random),
                                            random.uniform(-max_initial_random, max_initial_random),
                                            random.uniform(-max_initial_random, max_initial_random)))
            initial_surface_speed = view_speed - view_speed.project(normal)
            brush_color = self.get_brush_color(context)
            self.add_particle(index, location, brush_color, particle_settings, initial_surface_speed)
            return True        
        return False

    def add_particle(self, index, location, brush_color, particle_settings, initial_surface_speed):
        """ Add a single particle """
        if self.particles is not None:
            p = particle.Particle(location, brush_color, self.paint_mesh, particle_settings)
            p.speed = initial_surface_speed
            self.particles[index] = p
        else:
            p = self.simulator.create_particle(tuple(location), tuple(brush_color), tuple(initial_surface_speed),
                                               particle_settings)
            self.simulator.set_particle(index, p)

    def move_particles(self, deltaT, painticle_settings):
        """ Simulate gravity """
        if self.particles is not None:
            for i in range(len(self.particles) - 1, -1, -1):
                p = self.particles[i]
                p.move(painticle_settings.physics, self.paint_mesh, deltaT)
                if p.age > p.max_age:
                    del self.particles[i]
        else:
            sim_data = particle_simulator.SimulationData(deltaT, painticle_settings, self.paint_mesh, None)
            self.simulator.simulate(sim_data)

    
    def paint_particles(self, time_step: float):
        """ Paint all particles into the texture """
        if self.particles is not None:
            self.painter.draw(self.particles, time_step)
        else:
            self.painter.draw(self.simulator._particles, time_step)


    def undo_last_paint(self):
        self.painter.undo_last_paint()

    def clear_particles(self):
        """ Start with an empty set of particles """
        if self.particles is not None:
            self.particles = []
        else:
            self.simulator.clear_particles()

    def get_active_image(self, context: bpy.types.Context):
        """ Get the active image for painting """
        active_slot = context.object.active_material.paint_active_slot
        return context.object.active_material.texture_paint_images[active_slot]

    def get_brush_size(self, context: bpy.types.Context):
        """ Get the active brush size """
        return context.tool_settings.unified_paint_settings.size

    def get_brush_color(self, context: bpy.types.Context):
        """ Get the active brush size """
        return context.tool_settings.image_paint.brush.color

    def get_ray(self, context: bpy.types.Context, x, y):
        """ Get the ray under the mouse cursor """
        region = context.region
        rv3d = context.region_data
        coord = x-region.x, y-region.y

        # get the ray from the viewport and mouse
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        return ray_origin, ray_direction

    def ray_cast_on_object(self, ray_origin, ray_direction):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = self.matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_direction_obj = matrix_inv.to_3x3() @ ray_direction

        # cast the ray
        surface_info = self.paint_mesh.bvh.shoot_ray(ray_origin_obj, ray_direction_obj)
        if surface_info.tri_index != -1:
            return surface_info.location, surface_info.normal, surface_info.tri_index
        else:
            return None, None, None
