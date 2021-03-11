# Utilities for unit tests

import os
import bpy

def wait_for_debugger_attached():
    import debugpy
    # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
    debugpy.listen(5678)
    print("Waiting for debugger attach")
    debugpy.wait_for_client()

def open_file(filename):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    fullpath = os.path.join(script_dir, "testdata", filename)
    bpy.ops.wm.open_mainfile(filepath=fullpath)

def has_ui():
    """ Returns true, if blender supports running UI functionality, like creating GPU buffers """
    return not bpy.app.background

def no_ui():
    """ Returns true, if blender is running without UI functionality """
    return bpy.app.background