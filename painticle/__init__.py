# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from . import operator
from . import settings
from . import settings_panel
from . import physics
from . import preferences
from . import preferences_panel
from . import utils
import bpy

bl_info = {
    "name": "PAINTicle",
    "author": "Frank Firsching",
    "description": "Paint textures using particle systems",
    "blender": (2, 80, 0),
    "version": (0, 1, 0),
    "location": "",
    "warning": "",
    "category": "Paint"
}

classes = (
    operator.PaintOperator,
    physics.Physics,
    settings.Settings,
    settings_panel.ParticlePaintPresetsMenu,
    settings_panel.AddPresetParticleSettings,
    settings_panel.ParticlePaintMainPanel,
    settings_panel.ParticlePaintPhysicsPanel,
    preferences.Preferences,
    preferences_panel.PreferencesPanel
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.painticle_settings = bpy.props.PointerProperty(type=settings.Settings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.painticle_settings


if __name__ == "__main__":
    register()
