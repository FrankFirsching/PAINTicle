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

from .. import accel
from .. import numpyutils


class RepelStep(simulationstep.SimulationStep):
    def simulate(self, sim_data: simulationstep.SimulationData, particles: simulationstep.ParticleData,
                 forces: simulationstep.Forces, new_particles: simulationstep.ParticleData) -> simulationstep.Forces:
        factor = sim_data.settings.repulsion_factor
        repel_forces = accel.repel_forces(sim_data.hashed_grid, particles, factor, sim_data.timestep)
        urepel_forces = numpyutils.unstructured(repel_forces)
        uforces = numpyutils.unstructured(forces)
        return uforces + urepel_forces
