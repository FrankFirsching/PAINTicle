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


from . import settings
from . import sim
from . import ops
from . import ui

import bpy


bl_info = {
    "name": "PAINTicle",
    "author": "Frank Firsching",
    "description": "Paint textures using particle systems",
    "blender": (2, 92, 0),
    "version": (0, 1, 0),
    "location": "",
    "doc_url": "https://frankfirsching.github.io/PAINTicle/",
    "warning": "",
    "category": "Paint"
}

classes = (
    *settings.all_settings,
    *sim.all_steps,
    *ops.all_operators,
    *ui.all_ui
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.painticle_settings = bpy.props.PointerProperty(type=settings.core.Settings)
    ops.paintop.add_menu()
    ui.brushnodes.register_node_categories()


def unregister():
    ui.brushnodes.unregister_node_categories()
    ops.paintop.remove_menu()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.painticle_settings


if __name__ == "__main__":
    register()
