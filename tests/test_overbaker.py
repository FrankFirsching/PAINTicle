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

import bpy
import moderngl
import numpy as np
import pytest

from painticle import gpu_utils, meshbuffer, overbaker

from . import tstutils


@pytest.fixture
def test_mesh():
    tstutils.open_file('overbaker_test.blend')
    obj = bpy.data.objects['BakeGeo']
    mesh = obj.data
    mesh.calc_normals_split()
    mesh.calc_loop_triangles()
    return mesh


@pytest.mark.skipif(tstutils.no_validator(), reason="requires GLSL validator")
def test_glsl_validation_overbaker_init():
    vert, geom, frag = gpu_utils.load_shader_source("initoverbaker", ["utils"])
    assert gpu_utils.validate_glsl_shaders(vert, "vert")
    assert gpu_utils.validate_glsl_shaders(geom, "geom")
    assert gpu_utils.validate_glsl_shaders(frag, "frag")


@pytest.mark.skipif(tstutils.no_validator(), reason="requires GLSL validator")
def test_glsl_validation_overbaker_compute():
    comp = gpu_utils.load_shader_source("overbaker", ["utils"], ['comp'])
    assert gpu_utils.validate_glsl_shaders(comp, "comp")


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_overbaker(test_mesh):
    glcontext = moderngl.create_context()
    mesh_buffer = meshbuffer.MeshBuffer(glcontext, None)
    mesh_buffer.build_mesh_vbo(test_mesh)
    baker = overbaker.Overbaker(mesh_buffer, glcontext)
    assert baker is not None
    testshape = (16, 16, 4)
    tex_data = np.zeros(testshape, dtype='f4')
    tex_data[4:12, 4:12, 0] = np.arange(8)+1
    texture = glcontext.texture((16, 16), data=tex_data, components=4, dtype='f4')
    baker.overbake(texture, 3)
    overbaked = texture.read()
    overbaked = np.frombuffer(overbaked, dtype="f4")
    overbaked = overbaked.reshape(testshape)
    overbaked = overbaked[:, :, 0]
    overbaked_ref= [[0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 1.00, 1.07, 1.21, 1.57, 2.19, 3.04, 4.00, 5.00, 5.96, 6.81, 7.43, 7.79, 7.93, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.17, 1.46, 2.12, 3.00, 4.00, 5.00, 6.00, 6.88, 7.54, 7.83, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.41, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 7.59, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.00, 1.41, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 7.59, 8.00, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.00, 1.17, 1.46, 2.12, 3.00, 4.00, 5.00, 6.00, 6.88, 7.54, 7.83, 8.00, 8.00, 0.00],
                    [0.00, 1.00, 1.07, 1.21, 1.57, 2.19, 3.04, 4.00, 5.00, 5.96, 6.81, 7.43, 7.79, 7.93, 8.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]]
    assert len(overbaked) == len(overbaked_ref)
    for i in range(len(overbaked)):
        assert len(overbaked[i]) == len(overbaked_ref[i])
        assert tstutils.is_close_vec(overbaked[i], overbaked_ref[i], 0.01), f'on scanline {i}'
    