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

from . import simulationstep
from .. import numpyutils

import numpy as np
import mathutils
import random


class WindStep(simulationstep.SimulationStep):
    def __init__(self):
        self.last_shoot_time = 0
        self.rnd = random.Random()

    def simulate(self, sim_data: simulationstep.SimulationData, particles: simulationstep.ParticleData,
                 forces: simulationstep.Forces, new_particles: simulationstep.ParticleData) -> simulationstep.Forces:
        if sim_data.source_input is not None:
            input = sim_data.source_input
            wind_force = 10*(input.frame.direction - input.start_frame.direction)
            uforces = numpyutils.unstructured(forces)
            uforces += np.array(wind_force)[np.newaxis, :]
        return forces
