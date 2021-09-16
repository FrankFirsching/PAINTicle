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
from .interaction import Interactions, SourceInput


class Particles:
    """ A class managing the particle system for the paint operator """
    def __init__(self, context: bpy.types.Context, omit_painter=False):
        """ If omit_painter is True, paint_particles and undo_last_paint may not be called. """
        from . import particle_painter_gpu
        self.context = context
        self.rnd = random.Random()
        self.paint_mesh = trianglemesh.TriangleMesh(context)
        self.matrix = self.paint_mesh.object.matrix_world.copy()
        self.simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
        if omit_painter:
            self.painter = None
        else:
            self.painter = particle_painter_gpu.ParticlePainterGPU(context, self.simulator)
        self.input_data = None

    def __del__(self):
        if self.painter is not None:
            self.painter.shutdown()

    def numParticles(self):
        """ Return the number of simulated particles """
        return self.simulator.num_particles

    def interact(self, context: bpy.types.Context, event, interactions: Interactions):
        self.update_input_data(context, event, interactions, False)

    def start_interacting(self, context: bpy.types.Context, event, interactions: Interactions):
        self.update_input_data(context, event, interactions, True)
        self.simulator.setup_steps()

    def update_input_data(self, context: bpy.types.Context, event, interactions: Interactions,
                          reset_input_data: bool):
        brush_size = self.get_brush_size(context)
        origin, direction, size = self.get_ray(context, event.mouse_x, event.mouse_y, brush_size)
        pressure = event.pressure
        if reset_input_data:
            self.input_data = SourceInput(origin, direction, size, interactions, pressure)
        else:
            self.input_data.updateData(origin, direction, size, interactions, pressure)

    def move_particles(self, deltaT, painticle_settings):
        """ Simulate gravity """
        emit_settings = self.simulator.emit_settings()
        sim_data = particle_simulator.SimulationData(deltaT, emit_settings, painticle_settings, self.paint_mesh,
                                                     self.context, self.input_data)
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

    def get_ray(self, context: bpy.types.Context, x, y, brush_size):
        """ Get the ray under the mouse cursor """
        region = context.region
        rv3d = context.region_data
        coord = x-region.x, y-region.y
        coord_border = coord[0]+brush_size, coord[1]

        # get the ray from the viewport and mouse
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_direction_brush_border = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord_border)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        return ray_origin, ray_direction, (ray_direction_brush_border-ray_direction).length
