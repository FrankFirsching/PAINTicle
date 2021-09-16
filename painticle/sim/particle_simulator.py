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

import bpy
import bpy_types

from ..interaction import SourceInput
from .. import trianglemesh
from .. import settings


class SimulationData:
    """ The data a simulator needs on every time step """
    def __init__(self, timestep: float, emit_settings: settings.particlecreationsettings.ParticleCreationSettings,
                 settings: settings.core.Settings, paint_mesh: trianglemesh.TriangleMesh,
                 context: bpy_types.Context, source_input: SourceInput):
        self.timestep = timestep
        self.emit_settings = emit_settings
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
    def emit_settings(self):
        pass

    @abstractmethod
    def simulate(self, sim_data: SimulationData):
        pass
