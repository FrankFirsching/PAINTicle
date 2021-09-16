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

from bpy.props import StringProperty
from bpy.types import NodeTree


class BrushTree(NodeTree):
    '''A custom node tree type that allows defining PAINTicle particle brushes'''
    bl_idname = 'PAINTicleBrush'
    bl_label = "PAINTicle Brush"
    bl_icon = 'NODETREE'

    active_brush: StringProperty(name="Acive Brush name", description="The name of the active brush", default="",
                                 options=set())

    def get_active_brush_steps(self, initialize_steps=True, only_enabled=True):
        steps = []
        brush_node = self.nodes.get(self.active_brush)
        while brush_node is not None:
            # We can't check for "step" in brush_node, since this might return False in case the node is not
            # fully initialized yet by blender (e.g. never shown in the node editor). Asking for step will however
            # initialize the node fully and return the right step. This we check for the only type, that doesn't have a
            # step property.
            if brush_node.bl_idname != "BrushDefineNode":
                # During calculation of the simulation, steps might create temporary data,
                # Since blender is always allocating a new python object when getting the property group, we need
                # to get the object here first and then add the initialized one into the steps list. Otherwise those
                # temporary fields would disappear again.
                step = brush_node.step
                if step.enabled or not only_enabled:
                    if initialize_steps:
                        step.initialize()
                    steps.append(step)
            if 'brush' in brush_node.inputs and brush_node.inputs['brush'].is_linked:
                brush_node = brush_node.inputs['brush'].links[0].from_node
            else:
                brush_node = None
        steps.reverse()
        return steps

    def get_active_brush_nodes(self):
        nodes = []
        brush_node = self.nodes.get(self.active_brush)
        while brush_node is not None:
            # We can't check for "step" in brush_node, since this might return False in case the node is not
            # fully initialized yet by blender (e.g. never shown in the node editor). Asking for step will however
            # initialize the node fully and return the right step. This we check for the only type, that doesn't have a
            # step property.
            if brush_node.bl_idname != "BrushDefineNode":
                # During calculation of the simulation, steps might create temporary data,
                # Since blender is always allocating a new python object when getting the property group, we need
                # to get the object here first and then add the initialized one into the steps list. Otherwise those
                # temporary fields would disappear again.
                nodes.append(brush_node)
            if 'brush' in brush_node.inputs and brush_node.inputs['brush'].is_linked:
                brush_node = brush_node.inputs['brush'].links[0].from_node
            else:
                brush_node = None
        nodes.reverse()
        return nodes
