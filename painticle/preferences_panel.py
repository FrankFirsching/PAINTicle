# The panel showing the addon's preferences panel

# <pep8 compliant>

import bpy
from . import utils
from . import dependencies
from . import preferences

class PreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = preferences.id

    install_dependencies: dependencies.DependenciesProperty()

    # If this is changed, please also change preferences.get_instance()
    # Blender doesn't separate UI and data for preferences.
    painticle: bpy.props.PointerProperty(type=preferences.Preferences)

    def draw(self, context):
        row = self.layout.row()
        row.prop(self.painticle, "preview_threshold_edge")
        dependencies.draw_property(self, 'install_dependencies')
