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

from bpy.props import IntProperty
from bpy.types import PropertyGroup


id = __package__


def get_instance(context):
    """ Gets the blender managed instance of these preferences """
    global id
    # Unfortunately we need to reference a member of the preferences panel, since
    # blender doesn't separate UI and data for the preferences.
    return context.preferences.addons[id].preferences.painticle


class Preferences(PropertyGroup):
    """ The preferences object for the painticle add-on """
    preview_threshold_edge: IntProperty(name="Preview Mode Threshold",
                                        description="Performance option:\n"+
                                                    "Specifies the size of a square texture, that represents the " +
                                                    "largest image size still possible to simulate without falling " +
                                                    "back to preview mode.",
                                        default=1024, min=0, soft_min=0, soft_max=4096,
                                        options=set())
