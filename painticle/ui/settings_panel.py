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

import bpy
import bl_operators

from .. import settings
from ..ops.createdefaultbrushtree import CreateDefaultBrushTree
from ..ops.setactivebrushop import SetActiveBrushOp


class PAINTiclePanel:
    """ A mixin class for the concrete panels below """
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"


class PAINTiclePresetsMenu(bpy.types.Menu):
    """ A custom preset operator for the painticle panel """
    bl_idname = "OBJECT_MT_painticlepresetsmenu"
    bl_label = "PAINTicle Presets"
    preset_subdir = "scene/painticle_presets"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class AddPresetParticleSettings(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    '''Add a PAINTicle Settings Preset'''
    bl_idname = "scene.painticle_preset_add"
    bl_label = "Add PAINTicle Preset"
    preset_menu = "OBJECT_MT_painticlepresetsmenu"

    # variable used for all preset values
    preset_defines = [
        "obj = bpy.context.scene.painticle_settings"
    ]

    # properties to store in the preset
    preset_values = None

    # where to store the preset
    preset_subdir = "scene/painticle_presets"

    @classmethod
    def register(cls):
        # We can only initialize the preset_values attribute after the Settings class has been registered.
        AddPresetParticleSettings.preset_values = [
                "obj."+x for x in settings.core.Settings.bl_rna.properties.keys() if x != "rna_type"
            ]
        assert(len(AddPresetParticleSettings.preset_values) > 1)


class PAINTicleMainPanel(PAINTiclePanel, bpy.types.Panel):
    """ The main painticle panel, shown in the tool settings """
    bl_label = "PAINTicle"
    bl_idname = "PAINTICLE_PT_main_panel"
    bl_context = "imagepaint"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        row = layout.row(align=True)
        row.menu(PAINTiclePresetsMenu.bl_idname, text=PAINTiclePresetsMenu.bl_label)
        row.operator(AddPresetParticleSettings.bl_idname, text="", icon='ADD')
        row.operator(AddPresetParticleSettings.bl_idname, text="", icon='REMOVE').remove_active = True

        settings = context.scene.painticle_settings
        layout.prop(settings, "stop_painting_on_mouse_release")
        layout.template_ID(settings, "brush", new=CreateDefaultBrushTree.bl_idname)


class PAINTiclePhysicsPanel(PAINTiclePanel, bpy.types.Panel):
    """ A sub panel grouping the physics settings """
    bl_label = "Physics"
    bl_idname = "PAINTICLE_PT_physics_panel"
    bl_parent_id = "PAINTICLE_PT_main_panel"
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        physics = context.scene.painticle_settings.physics
        layout.prop(physics, "max_time_step")
        layout.prop(physics, "sim_sub_steps")


class PAINTicleBrushMenu(bpy.types.Menu):
    """ A custom preset operator for the painticle panel """
    bl_idname = "OBJECT_MT_painticlebrushmenu"
    bl_label = "PAINTicle Brush"
    
    def draw(self, context):
        layout = self.layout
        tree = context.scene.painticle_settings.brush
        if tree is not None:
            for n in tree.nodes:
                if n.bl_idname == "BrushDefineNode":
                    text = n.label if n.label != "" else n.name
                    op = layout.operator(SetActiveBrushOp.bl_idname, text=text)
                    op.node_group = tree.name
                    op.brush_to_activate = n.name


class PAINTicleBrushPanel(PAINTiclePanel, bpy.types.Panel):
    """ A sub panel grouping the brush settings """
    bl_label = "Brush"
    bl_idname = "PAINTICLE_PT_brush_panel"
    bl_parent_id = "PAINTICLE_PT_main_panel"
    bl_order = 3

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        brush_tree = context.scene.painticle_settings.brush
        if brush_tree is not None:
            active_brush = brush_tree.nodes.get(brush_tree.active_brush)
            text = PAINTicleBrushMenu.bl_label
            if active_brush is not None:
                text = active_brush.label if active_brush.label != "" else active_brush.name
            layout.menu(PAINTicleBrushMenu.bl_idname, text=text)
            nodes = brush_tree.get_active_brush_nodes()
            for node in nodes:
                box = layout.box()
                text = node.label if node.label != "" else node.name
                box.label(text=text)
                node.draw_buttons(context, box)
