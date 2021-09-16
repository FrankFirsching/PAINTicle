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

from .brushtree import BrushTreeNode, BrushNodeCategory, BrushSocket
from ..sim import brushstep, dragstep, frictionstep, gravitystep, rainstep, repelstep, windstep

import bpy
import nodeitems_utils
from bpy.types import Node


class BrushNode(BrushTreeNode):
    bl_label = "Brush"
    step: bpy.props.PointerProperty(type=brushstep.BrushStep)


class DragNode(BrushTreeNode):
    bl_label = "Drag"
    step: bpy.props.PointerProperty(type=dragstep.DragStep)


class FrictionNode(BrushTreeNode):
    bl_label = "Friction"
    step: bpy.props.PointerProperty(type=frictionstep.FrictionStep)


class GravityNode(BrushTreeNode):
    bl_label = "Gravity"
    step: bpy.props.PointerProperty(type=gravitystep.GravityStep)


class RainNode(BrushTreeNode):
    bl_label = "Rain"
    step: bpy.props.PointerProperty(type=rainstep.RainStep)


class RepelNode(BrushTreeNode):
    bl_label = "Repel"
    step: bpy.props.PointerProperty(type=repelstep.RepelStep)


class WindNode(BrushTreeNode):
    bl_label = "Wind"
    step: bpy.props.PointerProperty(type=windstep.WindStep)


class BrushDefineNode(Node):
    """ Base class for all custom nodes in the PAINTicleBrushTree tree type """
    bl_idname = "BrushDefineNode"
    bl_label = "Brush Define"

    active: bpy.props.BoolProperty(name="Active", description="Activate this brush definition.")

    @classmethod
    def poll(cls, ntree):
        """ Allow instantiation of our nodes only on the PAINTicle brush tree type """
        return BrushTreeNode.poll(ntree)

    def init(self, context):
        self.inputs.new(BrushSocket.bl_idname, "brush")

    def draw_buttons(self, context, layout):
        is_pressed = (self.id_data.active_brush == self.name)
        props = layout.operator("painticle.painticle_set_active_brush", text="Activate", depress=is_pressed)
        props.brush_to_activate = self.name


all_emitters = [BrushNode, RainNode]
all_physics = [DragNode, FrictionNode, GravityNode, RepelNode, WindNode]
all_system = [BrushDefineNode]
all_nodes = [*all_emitters, *all_physics, *all_system]


node_categories = [
    # identifier, label, items-list
    BrushNodeCategory('EMITTER', "Emitter", items=[
        nodeitems_utils.NodeItem(x.__name__) for x in all_emitters
    ]),
    BrushNodeCategory('PHYSICS', "Physics", items=[
        nodeitems_utils.NodeItem(x.__name__) for x in all_physics
    ]),
    BrushNodeCategory('SYSTEM', "System", items=[
        nodeitems_utils.NodeItem(x.__name__) for x in all_system
    ])
]


def register_node_categories():
    nodeitems_utils.register_node_categories('PAINTICLE_SIM_NODES', node_categories)


def unregister_node_categories():
    nodeitems_utils.unregister_node_categories('PAINTICLE_SIM_NODES')
