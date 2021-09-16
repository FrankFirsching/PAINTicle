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

from .physics import Physics
from .brushtree import BrushTree


class Settings(PropertyGroup):
    """ The settings object for the painticle tool """
    stop_painting_on_mouse_release: BoolProperty(name="Stop on mouse release",
                                                 description="If set to true, the particles immediately stop after " +
                                                             "painting.",
                                                 default=False,
                                                 options=set())
    physics: PointerProperty(type=Physics, name="Physics",
                             description="The physical properties of the simulation",
                             options=set())

    brush: PointerProperty(type=BrushTree, name="Brush",
                           description="The definition of the particle brush",
                           options=set())
