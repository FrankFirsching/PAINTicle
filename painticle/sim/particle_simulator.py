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

# The painting logic for the particles

# <pep8 compliant>

from abc import ABC
from abc import abstractmethod
import enum

import bpy
import bpy_types
import mathutils

from .. import trianglemesh
from .. import settings
from .. import utils


class Frame:
    def __init__(self, origin: mathutils.Vector, direction: mathutils.Vector):
        self.origin = origin
        self.up, self.right, self.direction = utils.orthogonalize(direction)


class Interactions(enum.Flag):
    NONE = 0
    EMIT_PARTICLES = enum.auto()


class SourceInput:
    """ A class storing the interactive inputs, during painting """
    def __init__(self, origin: mathutils.Vector = mathutils.Vector((0, 0, 0)),
                 direction: mathutils.Vector = mathutils.Vector((0, 0, 1)),
                 size: float = 1, interactions: Interactions = Interactions.NONE,
                 pressure: float = 1):
        self.updateData(origin, direction, size, interactions, pressure)
        self.start_frame = self.frame

    def updateData(self, origin: mathutils.Vector, direction: mathutils.Vector, size: float, interactions: Interactions,
                   pressure: float):
        self.frame = Frame(origin, direction)
        self.size = size
        self.interactions = interactions
        self.pressure = pressure


class SimulationData:
    """ The data a simulator needs on every time step """
    def __init__(self, timestep: float, settings: settings.Settings, paint_mesh: trianglemesh.TriangleMesh,
                 context: bpy_types.Context, source_input: SourceInput):
        self.timestep = timestep
        self.settings = settings
        self.paint_mesh = paint_mesh
        self.source_input = source_input
        self.hashed_grid = None
        self.context = context


class ParticleSimulator(ABC):
    """ The abstract base class representing the painting logic for the
        particles. This can be different logics, like GPU based painting or
        utilizing blender's own painting logic through some weired hacks on
        the uv editor. """

    context = None

    def __init__(self, context: bpy.types.Context):
        self.context = context

    @abstractmethod
    def shutdown(self):
        """ Called before the containing particles object is destroyed (e.g. be used to unregister draw callbacks) """
        pass

    @abstractmethod
    def clear_particles(self):
        pass

    @abstractmethod
    def simulate(self, sim_data: SimulationData):
        pass
