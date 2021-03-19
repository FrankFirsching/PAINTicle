# Testing the particle shader

# <pep8 compliant>

import pytest
import bpy
import gpu
import gpu_extras
import mathutils

import struct
import moderngl
import numpy as np

from particle_paint import gpu_utils

import tstutils


def test_shader_loading():
    source = gpu_utils.load_shader_source("particle", "frag")
    assert source is not None
    assert source.startswith("// Particle Paint shader")


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_draw_offscreen():
    width = 1024
    height = 1024
    glcontext = moderngl.create_context()
    framebuffer = gpu_utils.gpu_simple_framebuffer((width, height), glcontext)
    shader = gpu_utils.load_shader("particle", glcontext)
    assert shader is not None
    shader["particle_size"] = 0.05
    shader["image_size"] = (width, height)
    shader["color"] = (1, 0, 1)

    offset = 0.2
    coords = [0.5, 0.5,
              0.5+offset, 0.5,
              0.5-offset, 0.5,
              0.5, 0.5+offset,
              0.5, 0.5-offset]
    num_floats = len(coords)
    vbo_data = struct.pack(f"{num_floats}f", *coords)
    vbo = glcontext.buffer(vbo_data)
    vao = glcontext.vertex_array(shader, vbo, "uv")
    scope = glcontext.scope(framebuffer=framebuffer)
    with scope:
        glcontext.clear(0, 0, 0, 0)
        vao.render(moderngl.vertex_array.POINTS, num_floats//2)

    pixels = gpu_utils.read_pixel_data_from_framebuffer(width, height, framebuffer)
    gpu_utils.save_pixels("./debug.png", pixels, width, height)
