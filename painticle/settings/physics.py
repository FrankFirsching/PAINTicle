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

from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import FloatVectorProperty
from bpy.types import PropertyGroup


class Physics(PropertyGroup):
    """ The settings for the particle physics """

    max_time_step: FloatProperty(name="Max. timestep",
                                 description="The maximum time step used for the simulation.",
                                 default=0.04, options=set())

    sim_sub_steps: IntProperty(name="Simulation substeps",
                               description="The number of substeps to perform integration of the movement for the " +
                                           "particles.",
                               default=3, min=1, soft_max=16, options=set())
