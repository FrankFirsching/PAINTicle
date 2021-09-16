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

# The panel showing the addon's preferences panel

# <pep8 compliant>

import bpy
from .. import utils
from .. import dependencies
from ..settings import preferences


class PreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = preferences.id

    install_dependencies: dependencies.DependenciesProperty()

    # If this is changed, please also change preferences.get_instance()
    # Blender doesn't separate UI and data for preferences.
    painticle: bpy.props.PointerProperty(type=preferences.Preferences)

    def draw(self, context):
        layout = self.layout.column()
        layout.prop(self.painticle, "preview_threshold_edge")
        layout.prop(self.painticle, "preview_mode")
        layout.prop(self.painticle, "overlay_preview_opacity")
        layout.label(text="Version: "+utils.get_deployment_version())
        dependencies.draw_property(self, 'install_dependencies')
