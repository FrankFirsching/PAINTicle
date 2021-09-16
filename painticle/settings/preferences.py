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

from bpy.props import FloatProperty, IntProperty
from bpy.types import PropertyGroup
from bpy.props import EnumProperty


# Get the root level module name as our ID
id = __package__.split('.')[0]


def get_instance(context):
    """ Gets the blender managed instance of these preferences """
    global id
    # Unfortunately we need to reference a member of the preferences panel, since
    # blender doesn't separate UI and data for the preferences.
    return context.preferences.addons[id].preferences.painticle


class Preferences(PropertyGroup):
    """ The preferences object for the painticle add-on """
    preview_threshold_edge: IntProperty(name="Preview Mode Threshold",
                                        description="Performance option:\n" +
                                                    "Specifies the size of a square texture, that represents the " +
                                                    "largest image size still possible to simulate without falling " +
                                                    "back to preview mode.",
                                        default=1024, min=0, soft_min=0, soft_max=4096,
                                        options=set())
    preview_mode: EnumProperty(items=[("particles", "Particles",
                                       "Show just the particles", 1),
                                      ("texture_overlay", "Texture overlay",
                                       "Draw the highres texture with an overlay style", 2)],
                               name="Preview mode",
                               description="If the system needs to fallback to preview mode, how should be drawn.",
                               default="particles",
                               options=set())
    overlay_preview_opacity: FloatProperty(name="Overlay Preview Opacity",
                                           description="Opacity of the overlay, if preview mode is set to this.",
                                           default=0.5, min=0, max=1,
                                           options=set())
