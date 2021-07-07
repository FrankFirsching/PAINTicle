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

# Utilities for unit tests

import os
import subprocess
import bpy
import pytest


def fix_context():
    """Fix bpy.context if some command (like .blend import) changed/emptied it"""
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'window': window, 'screen': screen, 'area': area, 'region': region}
                        bpy.ops.screen.screen_full_area(override)
                        break


@pytest.fixture
def default_scene():
    bpy.ops.wm.read_homefile(use_factory_startup=True)
    # Need to call fix_context twice to restore the full screen area back to normal state
    fix_context()
    fix_context()


def open_file(filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    fullpath = os.path.join(script_dir, "testdata", filename)
    bpy.ops.wm.open_mainfile(filepath=fullpath)
    # Need to call fix_context twice to restore the full screen area back to normal state
    fix_context()
    fix_context()


class FakeContext(object):
    def setup_area_and_region(self):
        self.area = [x for x in self.screen.areas if x.type == "VIEW_3D"][0]
        self.region = [x for x in self.area.regions if x.type == "WINDOW"][0]
        self.region_data = [x for x in self.area.spaces if x.type == "VIEW_3D"][0].region_3d

    def setup_active_object(self, active_object):
        if active_object is not None:
            self.object = active_object
            self.active_object = active_object


def get_default_context(active_object=None):
    fake_context = FakeContext()
    # In some situations, the bpy.context.object is not accessible during the unit tests.
    # We fake it by using the active one from the first view layer.
    fake_context.object = bpy.context.scene.view_layers[0].objects.active
    for x in dir(bpy.context):
        setattr(fake_context, x, getattr(bpy.context, x))
    # Find a 3D view area to mimic the real usage, where the user triggers the addon by clicking a button in the 3D view
    fake_context.setup_area_and_region()
    fake_context.setup_active_object(active_object)
    return fake_context


class FakeEvent(object):
    def __init__(self, x, y):
        self.mouse_x = x
        self.mouse_y = y


def get_fake_event(x=0, y=0):
    return FakeEvent(x, y)


def has_ui():
    """ Returns true, if blender supports running UI functionality, like creating GPU buffers """
    return not bpy.app.background


def no_ui():
    """ Returns true, if blender is running without UI functionality """
    return bpy.app.background


_has_glslang_validator = None


def has_validator():
    """ Returns true, if the glslangValidator is supported by the system"""
    global _has_glslang_validator
    if _has_glslang_validator is None:
        try:
            devnull = open(os.devnull)
            subprocess.run(["glslangValidator", "-h"], stdout=devnull, stderr=devnull)
            _has_glslang_validator = True
        except OSError:
            _has_glslang_validator = False
    return _has_glslang_validator


def no_validator():
    return not has_validator()


def is_close(v1, v2, tolerance):
    return (v1 >= v2 - tolerance) and (v1 <= v2 + tolerance)


def is_close_vec(v1, v2, tolerance):
    return all(is_close(x, y, tolerance) for x, y in zip(v1, v2))
