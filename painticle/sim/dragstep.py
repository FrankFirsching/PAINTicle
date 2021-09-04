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


class DragStep(simulationstep.SimulationStep):
    def simulate(self, sim_data: simulationstep.SimulationData, particles: simulationstep.ParticleData,
                 forces: simulationstep.Forces, new_particles: simulationstep.ParticleData):
        physics = sim_data.settings.physics
        uspeed = numpyutils.unstructured(particles.speed)
        usize = numpyutils.unstructured(particles.size)
        avg_particle_size_sqr = sim_data.settings.particle_size * sim_data.settings.particle_size
        usize_sqr = usize * usize / avg_particle_size_sqr
        factor = physics.drag_coefficient * usize_sqr
        return forces - factor[:, np.newaxis] * uspeed
