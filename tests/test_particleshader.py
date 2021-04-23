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

from painticle import gpu_utils

import tstutils


def test_shader_loading():
    source = gpu_utils.load_shader_file("particle2d", "frag")
    assert source is not None
    assert source.startswith("// This file is part of PAINTicle.")


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_draw_offscreen():
    width = 1024
    height = 1024
    glcontext = moderngl.create_context()
    framebuffer = gpu_utils.gpu_simple_framebuffer((width, height), glcontext)
    shader = gpu_utils.load_shader("particle2d", glcontext, ["utils", "particle"])
    assert shader is not None
    shader["image_size"] = (width, height)
    shader["particle_size_age_factor"] = 2
    shader["time_step"] = 0.5
    shader["strength"] = 2

    offset = 0.2
    # Semantics of the values:
    #         uv                    size age+max  color
    coords = [0.5, 0.5,             50,  0.0, 1,  0.5, 0.5, 0.5,
              0.5+offset, 0.5,      75,  0.1, 1,  0.9, 0.2, 0.2,
              0.5-offset, 0.5,      25,  0.2, 1,  0.2, 0.9, 0.2,
              0.5, 0.5+offset,      50,  0.3, 1,  0.2, 0.2, 0.9,
              0.5, 0.5-offset,      50,  0.4, 1,  0.9, 0.2, 0.9
              ]
    num_floats = len(coords)
    vbo_data = struct.pack(f"{num_floats}f", *coords)
    vbo = glcontext.buffer(vbo_data)
    vao = glcontext.vertex_array(shader, vbo, "uv", "size", "age", "max_age", "color")
    scope = glcontext.scope(framebuffer=framebuffer)
    with scope:
        glcontext.clear(0, 0, 0, 0)
        vao.render(moderngl.vertex_array.POINTS, num_floats//2)

    pixels = gpu_utils.read_pixel_data_from_framebuffer(width, height, framebuffer)
    gpu_utils.save_pixels("./debug.png", pixels, width, height)


@pytest.mark.skipif(tstutils.no_validator(), reason="requires GLSL validator")
def test_glsl_validation_particle2d():
    vert, frag, geom = gpu_utils.load_shader_source("particle2d", ["utils", "particle"])
    assert gpu_utils.validate_glsl_shaders(vert, "vert")
    assert gpu_utils.validate_glsl_shaders(frag, "frag")
    assert gpu_utils.validate_glsl_shaders(geom, "geom")

@pytest.mark.skipif(tstutils.no_validator(), reason="requires GLSL validator")
def test_glsl_validation_particle3d():
    vert, frag, geom = gpu_utils.load_shader_source("particle3d", ["utils", "particle"])
    assert gpu_utils.validate_glsl_shaders(vert, "vert")
    assert gpu_utils.validate_glsl_shaders(frag, "frag")
    assert gpu_utils.validate_glsl_shaders(geom, "geom")
