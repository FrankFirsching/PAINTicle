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

from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty, PointerProperty
from bpy.types import PropertyGroup


class ParticleCreationSettings(PropertyGroup):
    flow_rate: FloatProperty(name="Number of particles per second",
                             description="Specifies the number of particles emitted per second from the brush.",
                             default=50, min=0.0, soft_min=0.0, soft_max=1000,
                             options=set())

    particle_size: FloatProperty(name="Particle size",
                                 description="The maximum size of an individual particle.",
                                 default=0.03, min=0.0, soft_min=0.0, soft_max=0.1,
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
                        default=0.4, min=0.0, soft_min=0.0, soft_max=100,
                        options=set())

    mass_random: FloatProperty(name="Mass randomization",
                               description="The possible mass variation of the particles.",
                               default=0.1, min=0.0, soft_min=0.0, soft_max=100,
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

    initial_speed: FloatProperty(name="Initial speed",
                                 description="The initial speed of the particles, when they are born.",
                                 min=0.0, soft_max=1, default=0.0, options=set())

    initial_speed_random: FloatProperty(name="Initial speed randomization",
                                        description="The random factor of the initial speed.",
                                        min=0.0, max=1, default=0.0, options=set())
