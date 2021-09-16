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

from bpy.props import FloatVectorProperty
import numpy as np


class GravityStep(simulationstep.SimulationStep):

    gravity: FloatVectorProperty(name="Gravity",
                                 description="The gravitational force applied to the particles.",
                                 default=(0, 0, -9.81),
                                 subtype="ACCELERATION", unit="ACCELERATION",
                                 options=set())


    def simulate(self, sim_data: simulationstep.SimulationData, particles: simulationstep.ParticleData,
                 forces: simulationstep.Forces, new_particles: simulationstep.ParticleData) -> simulationstep.Forces:
        gravity = np.array(self.gravity)
        mass = numpyutils.unstructured(particles.mass)
        return forces + mass[:, np.newaxis] * gravity[np.newaxis, :]
