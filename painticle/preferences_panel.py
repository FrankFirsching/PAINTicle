# The panel showing the addon's preferences panel

# <pep8 compliant>

import bpy
from . import utils
from . import dependencies


class PreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = __package__

    install_dependencies: dependencies.DependenciesProperty()

    def draw(self, context):
        dependencies.draw_property(self, 'install_dependencies')
