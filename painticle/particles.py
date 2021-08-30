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

from bpy_extras import view3d_utils
import bpy

import math
import random

from . import trianglemesh
from .sim import particle_simulator_cpu
from .sim import particle_simulator


class Particles:
    """ A class managing the particle system for the paint operator """
    def __init__(self, context: bpy.types.Context, omit_painter=False):
        """ If omit_painter is True, paint_particles and undo_last_paint may not be called. """
        from . import particle_painter_gpu
        self.rnd = random.Random()
        self.paint_mesh = trianglemesh.TriangleMesh(context)
        self.matrix = self.paint_mesh.object.matrix_world.copy()
        self.simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
        if omit_painter:
            self.painter = None
        else:
            self.painter = particle_painter_gpu.ParticlePainterGPU(context, self.simulator.hashed_grid)
        self.last_shoot_time = 0

    def __del__(self):
        if self.painter is not None:
            self.painter.shutdown()

    def numParticles(self):
        """ Return the number of simulated particles """
        return self.simulator.num_particles

    def shoot(self, context: bpy.types.Context, event, delta_t, painticle_settings):
        """ Shoot particles according to the flow rate """
        time_between_particles = 1/painticle_settings.flow_rate
        self.last_shoot_time += delta_t
        num_particles_to_shoot = int(self.last_shoot_time / time_between_particles)
        ray_origins, ray_directions = self.create_ray_data(num_particles_to_shoot, context, event)
        brush_color = self.get_brush_color(context)
        self.simulator.add_particles_from_rays(ray_origins, ray_directions, self.paint_mesh.bvh, self.matrix,
                                               brush_color, painticle_settings)
        self.last_shoot_time -= num_particles_to_shoot*time_between_particles

    def create_ray_data(self, num_rays, context: bpy.types.Context, event):
        ray_origins = []
        ray_directions = []
        brush_size = self.get_brush_size(context)
        for _ in range(num_rays):
            angle = 2*math.pi*self.rnd.random()
            distance = brush_size*self.rnd.random()
            offset_x = math.cos(angle)*distance
            offset_y = math.sin(angle)*distance
            ray_origin, ray_direction = self.get_ray(context,
                                                     event.mouse_x+offset_x,
                                                     event.mouse_y+offset_y)
            ray_origins.append(ray_origin)
            ray_directions.append(ray_direction)
        return ray_origins, ray_directions

    def move_particles(self, deltaT, painticle_settings):
        """ Simulate gravity """
        sim_data = particle_simulator.SimulationData(deltaT, painticle_settings, self.paint_mesh, None)
        self.simulator.simulate(sim_data)

    def paint_particles(self, time_step: float):
        """ Paint all particles into the texture """
        self.painter.draw(self.simulator._particles, time_step)

    def undo_last_paint(self):
        self.painter.undo_last_paint()

    def clear_particles(self):
        """ Start with an empty set of particles """
        self.simulator.clear_particles()

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
