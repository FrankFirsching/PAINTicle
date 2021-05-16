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


def wait_for_debugger_attached():
    import debugpy
    # 5678 is the default attach port in the VS Code debug configurations.
    # Unless a host and port are specified, host defaults to 127.0.0.1
    debugpy.listen(5678)
    print("Waiting for debugger attach")
    debugpy.wait_for_client()


@pytest.fixture
def default_scene():
    bpy.ops.wm.read_homefile(use_factory_startup=True)


def open_file(filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    fullpath = os.path.join(script_dir, "testdata", filename)
    bpy.ops.wm.open_mainfile(filepath=fullpath)


class FakeContext(object):
    def setup_screen_and_area(self):
        self.screen = bpy.data.screens['Layout']
        self.area = [x for x in self.screen.areas if x.type == "VIEW_3D"][0]


def get_default_context():
    fake_context = FakeContext()
    # In some situations, the bpy.context.object is not accessible during the unit tests.
    # We fake it by using the active one from the first view layer.
    fake_context.object = bpy.context.scene.view_layers[0].objects.active
    for x in dir(bpy.context):
        setattr(fake_context, x, getattr(bpy.context, x))
    # Find a 3D view area to mimic the real usage, where the user triggers the addon by clicking a button in the 3D view
    fake_context.setup_screen_and_area()
    return fake_context


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
