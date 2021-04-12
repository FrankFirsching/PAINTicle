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

import bpy
import bl_operators

from . import settings

class ParticlePaintPanel:
    """ A mixin class for the concrete panels below """
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_options = {"DEFAULT_CLOSED"}


class ParticlePaintPresetsMenu(bpy.types.Menu):
    """ A custom preset operator for the painticle panel """
    bl_idname = "OBJECT_MT_particlepaintpresetsmenu"
    bl_label = "PAINTicle Presets"
    preset_subdir = "scene/painticle_presets"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class AddPresetParticleSettings(bl_operators.presets.AddPresetBase, bpy.types.Operator):
    '''Add a PAINTicle Settings Preset'''
    bl_idname = "scene.painticle_preset_add"
    bl_label = "Add PAINTicle Preset"
    preset_menu = "OBJECT_MT_particlepaintpresetsmenu"

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
                "obj."+x for x in settings.Settings.bl_rna.properties.keys() if x != "rna_type"
            ]
        assert(len(AddPresetParticleSettings.preset_values) > 1)


class ParticlePaintMainPanel(ParticlePaintPanel, bpy.types.Panel):
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
        row.menu(ParticlePaintPresetsMenu.bl_idname, text=ParticlePaintPresetsMenu.bl_label)
        row.operator(AddPresetParticleSettings.bl_idname, text="", icon='ADD')
        row.operator(AddPresetParticleSettings.bl_idname, text="", icon='REMOVE').remove_active = True

        settings = context.scene.painticle_settings
        layout.prop(settings, "flow_rate")
        layout.prop(settings, "particle_size")
        layout.prop(settings, "particle_size_random")
        layout.prop(settings, "particle_size_age_factor")
        layout.prop(settings, "mass")
        layout.prop(settings, "mass_random")
        layout.prop(settings, "max_age")
        layout.prop(settings, "max_age_random")
        layout.prop(settings, "color_random")
        layout.prop(settings, "stop_painting_on_mouse_release")

class ParticlePaintPhysicsPanel(ParticlePaintPanel, bpy.types.Panel):
    """ A sub panel grouping the physics settings """
    bl_label = "Physics"
    bl_idname = "PAINTICLE_PT_physics_panel"
    bl_parent_id = "PAINTICLE_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        physics = context.scene.painticle_settings.physics
        layout.prop(physics, "gravity")
        layout.prop(physics, "initial_speed")
        layout.prop(physics, "initial_speed_random")
        layout.prop(physics, "friction_coefficient")
        layout.prop(physics, "max_time_step")
