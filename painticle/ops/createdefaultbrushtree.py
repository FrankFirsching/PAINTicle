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

from bpy.types import NodeSocket
from ..settings.brushtree import BrushTree
import bpy


def _create_next_step(type, prev_step, tree):
    node = tree.nodes.new(type)
    if type.endswith("Node"):
        node.label = type[:-4]  # Cut off "Node from type name"
    else:
        node.label = type
    if prev_step is not None:
        node.location = prev_step.location
        node.location[0] += 50+prev_step.width
        tree.links.new(node.inputs['brush'], prev_step.outputs['brush'])
    return node


def create_default_brush_tree():
    tree = bpy.data.node_groups.new("Default Brushes", BrushTree.bl_idname)

    brush = _create_next_step("BrushNode", None, tree)
    gravity = _create_next_step("GravityNode", brush, tree)
    repel = _create_next_step("RepelNode", gravity, tree)
    drag = _create_next_step("DragNode", repel, tree)
    friction = _create_next_step("FrictionNode", drag, tree)
    brush_define = _create_next_step("BrushDefineNode", friction, tree)
    brush_define.label = "Paint Brush"
    tree.active_brush = brush_define.name

    rain = _create_next_step("RainNode", None, tree)
    rain.step.creation_settings.flow_rate = 2500
    rain.step.creation_settings.mass = 0.3
    rain.step.creation_settings.max_age = 0.5
    rain.step.creation_settings.max_age_random = 0.2
    rain.location[1] = 400
    gravity = _create_next_step("GravityNode", rain, tree)
    wind = _create_next_step("WindNode", gravity, tree)
    wind.step.enabled = False
    repel = _create_next_step("RepelNode", wind, tree)
    drag = _create_next_step("DragNode", repel, tree)
    friction = _create_next_step("FrictionNode", drag, tree)
    brush_define = _create_next_step("BrushDefineNode", friction, tree)
    brush_define.label = "Rain Brush"

    bpy.context.scene.painticle_settings.brush = tree


class CreateDefaultBrushTree(bpy.types.Operator):
    """Create the default brush node tree"""
    bl_idname = "scene.create_default_brush_tree"
    bl_label = "PAINTicle Create default brush"
    # bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED'}
    bl_undo_group = "ParticlePaint"

    def __init__(self):
        pass

    def execute(self, context):
        create_default_brush_tree()
        return {'FINISHED'}
