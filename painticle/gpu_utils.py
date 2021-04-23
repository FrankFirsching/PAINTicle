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

# Generic blender gpu addons

# <pep8 compliant>

import bpy
import os
import numpy as np
import typing
import subprocess

from . import dependencies

import moderngl


def image_sizes(image):
    """ Thus function shall return all images sizes of all UDIM tiles. However
        currently blender doesn't allow access to the tiles, except their names.
        So we can only work with untiles images """
    return [image.size] if image is not None else [(0, 0)]


def max_image_size(image):
    """ Thus function shall return the combined maximum images size of all UDIM tiles. However
        currently blender doesn't allow access to the tiles, except their names.
        So we can only work with untiles images """
    sizes = image_sizes(image)
    width = max([s[0] for s in sizes])
    height = max([s[1] for s in sizes])
    return width, height


def gpu_framebuffer_for_image(image, glcontext: moderngl.Context):
    size = max_image_size(image)
    return gpu_simple_framebuffer(size, glcontext)


def gpu_simple_framebuffer(size, glcontext: moderngl.Context) -> moderngl.Framebuffer:
    color_attachment = glcontext.texture(size, components=4, dtype="f4")
    return glcontext.framebuffer(color_attachment)


def load_shader_file(shader_name: str, stage: str) -> str:
    """ Loads the shader source from the addon's resources directory. Possible stages are
        * 'vert' = vertex shader
        * 'geom' = geometry shader
        * 'frag' = fragment shader
        * 'def' = definitions for each stage
    """
    basepath = os.path.dirname(os.path.realpath(__file__))
    stage_addition = "" if stage is None or stage == "" else "_"+stage
    full_file_name = os.path.join(basepath, "shaders", shader_name+stage_addition+".glsl")
    if not os.path.exists(full_file_name):
        return None
    with open(full_file_name) as f:
        return f.read()


def _join_shader(definitions_shader, specific_shader, prepend_version=True):
    version = "#version 430\n" if prepend_version else ""
    if prepend_version and specific_shader is None:
        # On the last stage of concatenation, if specific shader is None, then also return None
        return None
    use_definition = definitions_shader+"\n" if definitions_shader is not None else ""
    use_specific = specific_shader if specific_shader is not None else ""
    return version + use_definition + use_specific


def load_shader_source(shader_name, additional_libs: typing.Iterable[str] = None) -> typing.Tuple:
    """ Load all shaders for a given shader name and return a triple with the preprocessed sources """
    vertex_shader = load_shader_file(shader_name, "vert")
    geometry_shader = load_shader_file(shader_name, "geom")
    fragment_shader = load_shader_file(shader_name, "frag")
    definitions_shader = load_shader_file(shader_name, "def")
    if additional_libs is not None:
        for lib in reversed(additional_libs):
            definitions_shader = _join_shader(load_shader_file(lib, "def"), definitions_shader, False)
    vertex_shader = _join_shader(definitions_shader, vertex_shader)
    fragment_shader = _join_shader(definitions_shader, fragment_shader)
    geometry_shader = _join_shader(definitions_shader, geometry_shader)
    return vertex_shader, fragment_shader, geometry_shader


def load_shader(shader_name, glcontext: moderngl.Context,
                additional_libs: typing.Iterable[str] = None) -> moderngl.Program:
    """ Load all shaders for a given shader name and return a compiled shader program """
    vertex_shader, fragment_shader, geometry_shader = load_shader_source(shader_name, additional_libs)
    program = glcontext.program(vertex_shader=vertex_shader,
                                fragment_shader=fragment_shader,
                                geometry_shader=geometry_shader)
    return program


def read_pixel_data_from_framebuffer(width, height, framebuffer: moderngl.Framebuffer):
    """ Read the pixel from the current back buffer """
    buffer = np.empty(width*height*4, np.float32)
    framebuffer.read_into(buffer, components=4, dtype='f4')
    return buffer


def save_pixels(filepath, pixel_data, width, height):
    """ Save an image given by pixels, e.g. read from the back buffer """
    image = bpy.data.images.new("paticle_paint_temp", width, height, alpha=True)
    image.filepath = filepath
    image.pixels.foreach_set(pixel_data)
    image.save()
    bpy.data.images.remove(image)


def trigger_redraw():
    """ Triggers a redraw in all image and 3D views """
    for area in bpy.context.screen.areas:
        if area.type in ['IMAGE_EDITOR', 'VIEW_3D']:
            area.tag_redraw()


def print_shader_members(shader: moderngl.Program):
    """ A debugging function, printing all varyings and uniforms of a shader program """
    for name in shader:
        member = shader[name]
        print(name, type(member), member)


def validate_glsl_shaders(full_shader_source, stage):
    """ A utility, that validates a glsl shader source through the Khronos reference validator.
        The validator needs to be installed on the system and callable without specifying the installatio path """
    if full_shader_source is None:
        # A non existent shader is valid (e.g. geometry stage)
        return True
    proc = subprocess.run(['glslangValidator', '--stdin', '-S', stage], input=full_shader_source, text=True,
                          capture_output=True)
    if proc.returncode != 0:
        print("\n".join([str(i+1)+": "+x for i, x in enumerate(full_shader_source.split('\n'))]))
        output = proc.stdout
        if output.startswith("stdin"):
            output = output[5:]
        print(output)
    return proc.returncode == 0
