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

from bpy.props import FloatProperty
from bpy.props import BoolProperty
from bpy.props import FloatVectorProperty
from bpy.props import PointerProperty
from bpy.types import PropertyGroup
from painticle.physics import Physics


class Settings(PropertyGroup):
    """ The settings object for the painticle tool """
    flow_rate: FloatProperty(name="Number of particles per second",
                             description="Specifies the number of particles emitted per second from the brush.",
                             default=50, min=0.0, soft_min=0.0, soft_max=100,
                             options=set())
    particle_size: FloatProperty(name="Particle size",
                                 description="The maximum size of an individual particle.",
                                 default=0.02, min=0.0, soft_min=0.0, soft_max=0.1,
                                 options=set())
    particle_size_random: FloatProperty(name="Particle size randomization",
                                        description="The possible size variation of the particles.",
                                        default=0.01, min=0.0, soft_min=0.0, soft_max=0.1,
                                        options=set())
    particle_size_age_factor: FloatProperty(name="Particle size age factor",
                                            description="Multiplier of the particle's size dependent on the age.\n" +
                                                        "<1 makes the particle smaller over time.\n" +
                                                        "=1 keeps the size.\n" +
                                                        ">1 makes it larger.",
                                            default=1, min=0, max=2,
                                            options=set())
    mass: FloatProperty(name="Mass",
                        description="The average mass of a single particle.",
                        default=1, min=0.0, soft_min=0.0, soft_max=100,
                        options=set())
    mass_random: FloatProperty(name="Mass randomization",
                               description="The possible mass variation of the particles.",
                               default=0.2, min=0.0, soft_min=0.0, soft_max=100,
                               options=set())
    max_age: FloatProperty(name="Maximum age",
                           description="The maximum age of an individual particle.",
                           default=2, min=0.0, soft_min=0.0, soft_max=100,
                           options=set())
    max_age_random: FloatProperty(name="Maximum age randomization",
                                  description="The age variation of an individual particle.",
                                  default=1, min=0.0, soft_min=0.0, soft_max=100,
                                  options=set())
    color_random: FloatVectorProperty(name="Color randomization",
                                      description="The color variation of an individual particle applied in HSV mode.",
                                      subtype="COLOR_GAMMA", default=(0.3, 0.25, 0.2), min=0, max=1,
                                      options=set())
    repulsion_factor: FloatProperty(name="Repulsion factor",
                                    description="A factor, that influences the repulsion effect between the particles.",
                                    default=0.2, min=0, soft_max=2,
                                    options=set())
    stop_painting_on_mouse_release: BoolProperty(name="Stop on mouse release",
                                                 description="If set to true, the particles immediately stop after " +
                                                             "painting.",
                                                 default=False,
                                                 options=set())
    physics: PointerProperty(type=Physics, name="Physics",
                             description="The physical properties of the simulation",
                             options=set())
