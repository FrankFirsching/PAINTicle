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

import particle_paint.operator
import particle_paint.settings
import particle_paint.panel
import bpy

bl_info = {
    "name" : "ParticlePaint",
    "author" : "Frank Firsching",
    "description" : "Paint textures using particle systems",
    "blender" : (2, 80, 0),
    "location" : "",
    "warning" : "",
    "category" : "Paint"
}

classes = (
    particle_paint.operator.PaintOperator,
    particle_paint.physics.Physics,
    particle_paint.settings.Settings,
    particle_paint.panel.ParticlePaintMainPanel,
    particle_paint.panel.ParticlePaintPhysicsPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.particle_paint_settings = bpy.props.PointerProperty(type=particle_paint.settings.Settings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.particle_paint_settings

if __name__ == "__main__":
    register()
