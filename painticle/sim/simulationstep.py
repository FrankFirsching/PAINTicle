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

from . import particle_simulator
from .. import accel

import numpy as np


# Define some datatypes used in the simulation step locally
SimulationData = particle_simulator.SimulationData
ParticleData = accel.ParticleData
Forces = np.array


class SimulationStep(ABC):
    @abstractmethod
    def simulate(self, sim_data: SimulationData, particles: ParticleData, forces: Forces, new_particles: ParticleData):
        pass

    