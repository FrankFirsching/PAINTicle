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

from ..settings.brushtree import BrushTree
import bpy
from bpy.props import StringProperty


class SetActiveBrushOp(bpy.types.Operator):
    """Set the active brush"""
    bl_idname = "painticle.painticle_set_active_brush"
    bl_label = "PAINTicle Set active brush"
    # bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED'}
    bl_undo_group = "ParticlePaint"

    node_group: StringProperty(name="Node group id, that contains the brush")
    brush_to_activate: StringProperty(name="Brush to activate")

    def __init__(self):
        pass

    def execute(self, context):
        node_group = bpy.data.node_groups.get(self.node_group)
        if node_group is None and hasattr(context, "node"):
            node_group = context.node.id_data
        if node_group is None:
            raise RuntimeError("Invalid node group specified.")
        if node_group.bl_idname != BrushTree.bl_idname:
            raise RuntimeError("Provided node group is not a PAINTicle tree.")
        node_group.active_brush = self.brush_to_activate
        return {'FINISHED'}
