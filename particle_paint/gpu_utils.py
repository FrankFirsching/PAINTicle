# Generic blender gpu addons

import bpy
import os
import numpy as np

from . import dependencies

import moderngl

def image_sizes(image):
    """ Thus function shall return all images sizes of all UDIM tiles. However
        currently blender doesn't allow access to the tiles, except their names.
        So we can only work with untiles images """
    return [image.size] if image is not None else [(0,0)]


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
    #color_attachment = glcontext.renderbuffer(size)
    color_attachment = glcontext.texture(size, components=4, dtype="f4")
    return glcontext.framebuffer(color_attachment)


def load_shader_source(shader_name: str, stage: str) -> str:
    """ Loads the shader source from the addon's resources directory. Possible stages are
        * 'vert' = vertex shader
        * 'geom' = geometry shader
        * 'frag' = fragment shader
    """
    basepath = os.path.dirname(os.path.realpath(__file__))
    full_file_name = os.path.join(basepath, "shaders", shader_name+"_"+stage+".glsl")
    if not os.path.exists(full_file_name):
        return None
    with open(full_file_name) as f:
        return f.read()


def _join_shader(definitions_shader, specific_shader):
    version = "#version 330"
    if definitions_shader is None:
        return version + "\n" + specific_shader
    else:
        return version + "\n" + definitions_shader + "\n" + specific_shader


def load_shader(shader_name, glcontext: moderngl.Context) -> moderngl.Program:
    """ Load all shaders for a given shader name """
    vertex_shader = load_shader_source(shader_name, "vert")
    geometry_shader = load_shader_source(shader_name, "geom")
    fragment_shader = load_shader_source(shader_name, "frag")
    definitions_shader = load_shader_source(shader_name, "def")
    program = glcontext.program(vertex_shader=_join_shader(definitions_shader, vertex_shader),
                                fragment_shader=_join_shader(definitions_shader, fragment_shader),
                                geometry_shader=_join_shader(definitions_shader, geometry_shader),
                                )
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