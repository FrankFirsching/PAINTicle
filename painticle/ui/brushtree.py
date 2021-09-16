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

from bpy.props import IntProperty
from bpy.types import Node, NodeSocket
from nodeitems_utils import NodeCategory

from ..sim.emitterstep import EmitterStep
from ..settings.brushtree import BrushTree
from ..settings.particlecreationsettings import ParticleCreationSettings


class BrushSocket(NodeSocket):
    '''Custom node simulation socket type'''
    bl_idname = 'PAINTicleBrushSocket'
    bl_label = "Simulation Socket"

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 1)


class BrushTreeNode(Node):
    """ Base class for all custom nodes in the PAINTicleBrushTree tree type """
    step: None

    @classmethod
    def poll(cls, ntree):
        """ Allow instantiation of our nodes only on the PAINTicle brush tree type """
        return ntree.bl_idname == BrushTree.bl_idname

    def init(self, context):
        if not isinstance(self.step, EmitterStep):
            self.inputs.new(BrushSocket.bl_idname, "brush")
        self.outputs.new(BrushSocket.bl_idname, "brush")
        self.width = 250

    def draw_buttons(self, context, layout):
        if hasattr(self, "step"):
            self._draw_step_buttons(self.step.__class__, self.step, layout)
        else:
            layout.label(text=f"{self.bl_label} does not define which step it represents.")

    def _draw_step_buttons(self, cls, obj, layout):
        for base in cls.__bases__:
            self._draw_step_buttons(base, obj, layout)
        if hasattr(cls, "__annotations__"):
            for prop in self._get_annotations(cls):
                prop_value = getattr(obj, prop)
                if isinstance(prop_value, ParticleCreationSettings):
                    self._draw_step_buttons(prop_value.__class__, prop_value, layout)
                else:
                    layout.prop(obj, prop)

    def _get_annotations(self, o):
        if isinstance(o, type):
            return o.__dict__.get('__annotations__', [])
        else:
            return getattr(o, '__annotations__', [])


# Node Categories
class BrushNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == BrushTree.bl_idname
