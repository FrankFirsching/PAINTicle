# Utilities for unit tests

import os
import bpy
import pytest


def wait_for_debugger_attached():
    import debugpy
    # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
    debugpy.listen(5678)
    print("Waiting for debugger attach")
    debugpy.wait_for_client()


@pytest.fixture
def default_scene():
    open_file("default_scene.blend")


def open_file(filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    fullpath = os.path.join(script_dir, "testdata", filename)
    bpy.ops.wm.open_mainfile(filepath=fullpath)


class FakeContext(object):
    pass


def get_default_context():
    fake_context = FakeContext()
    # In some situations, the bpy.context.object is not accessible during the unit tests.
    # We fake it by using the active one from the first view layer.
    fake_context.object = bpy.context.scene.view_layers[0].objects.active
    for x in dir(bpy.context):
        setattr(fake_context, x, getattr(bpy.context, x))
    return fake_context

def has_ui():
    """ Returns true, if blender supports running UI functionality, like creating GPU buffers """
    return not bpy.app.background


def no_ui():
    """ Returns true, if blender is running without UI functionality """
    return bpy.app.background


def is_close(v1, v2, tolerance):
    return  (v1 >= v2 - tolerance) and (v1 <= v2 + tolerance)
