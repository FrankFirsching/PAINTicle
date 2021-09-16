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

from bpy.props import FloatProperty
import numpy as np


class FrictionStep(simulationstep.SimulationStep):

    friction_coefficient: FloatProperty(name="Friction",
                                        description="The friction coefficient (how sticky is the surface).",
                                        min=0.0, soft_max=0.1, default=0.01, options=set())

    def simulate(self, sim_data: simulationstep.SimulationData, particles: simulationstep.ParticleData,
                 forces: simulationstep.Forces, new_particles: simulationstep.ParticleData):
        # Friction calculation
        # Project forces onto normal vector
        # We don't need to divide by the square length of normal, since this is a normalized vector.
        unormal = numpyutils.unstructured(particles.normal)
        factor = numpyutils.vec_dot(unormal, forces)
        ortho_force = unormal * factor[:, np.newaxis]
        # The force on the plane is then just simple vector subtraction
        plane_force = forces - ortho_force
        # factor is the inverse of what we need here, since the normal is pointing to the outside of the surface,
        # but friction only applies if force is applied towards the surface. Hence we use (1+x) instead of (1-x)
        friction = np.clip(1+self.friction_coefficient*factor/numpyutils.vec_length(plane_force), 0, 1)
        return plane_force * friction[:, np.newaxis]
