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

import pytest
import bgl
import gpu
import gpu_extras.batch
import numpy as np

from painticle import accel, gpu_utils, numpyutils

from . import tstutils


def test_construction():
    grid = accel.HashedGrid(1)
    assert grid is not None
    assert grid.voxel_size == 1
    x = 10
    y = 14
    z = 53
    # Check no symmetry
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([-x, y, z])
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x, -y, z])
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x, y, -z])
    # Check varying for small changes
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x+1, y, z])
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x-1, y, z])
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x, y+1, z])
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x, y-1, z])
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x, y, z+1])
    assert grid.hash_grid([x, y, z]) != grid.hash_grid([x, y, z-1])


def test_data_access():
    grid = accel.HashedGrid(1)
    assert grid is not None
    points = [[0,   0, 0],
              [1,   1, 1],
              [2,   2, 2],
              [1.5, 1, 1]]
    grid.build(points)
    sorted_ids = grid.sorted_particle_ids
    offsets = grid.cell_offsets
    filled_cell_ids = set()
    for i in range(len(points)):
        cell_id = sorted_ids[i][0]
        particle_id = sorted_ids[i][1]
        assert cell_id == grid.hash_coord(points[particle_id])
        filled_cell_ids.add(cell_id)
    assert len(filled_cell_ids) == 3  # 2 points shall be filling the same cell
    for i, offset in enumerate(offsets):
        if i in filled_cell_ids:
            assert offset != accel.id_none
        else:
            assert offset == accel.id_none


vert_source = """
in vec2 pos;
void main() {
    gl_Position = vec4(pos,0,1);
}
"""


bucket_frag = """
#extension GL_ARB_shading_language_packing : enable
out vec4 frag_color;
uniform int z;
uniform int screen_size;
layout(pixel_center_integer) in vec4 gl_FragCoord;
void main() {
   ivec2 pixel = ivec2(gl_FragCoord.xy) - screen_size / 2;
   frag_color = unpackUnorm4x8(hashGrid(ivec3(pixel, z)));
}
"""


coord_frag = """
#extension GL_ARB_shading_language_packing : enable
out vec4 frag_color;
uniform int z;
uniform int screen_size;
layout(pixel_center_integer) in vec4 gl_FragCoord;
void main() {
   vec2 coord = vec2(gl_FragCoord.xy+0.5) - screen_size / 2;
   frag_color = unpackUnorm4x8(hashCoord(vec3(coord, z+0.5), 1));
}
"""


def perform_gpu_test(frag_source, cpu_func):
    grid = accel.HashedGrid(1)
    assert grid is not None
    hash_grid_glsl = gpu_utils.load_shader_file("gridhash", "def")
    shader = gpu.types.GPUShader(vert_source, frag_source, libcode=hash_grid_glsl)
    screen_size = 128
    offscreen = gpu.types.GPUOffScreen(screen_size, screen_size)
    points = [[-1, -1], [-1, 1], [1, 1], [1, -1]]
    indices = ((0, 1, 2), (2, 3, 0))
    batch = gpu_extras.batch.batch_for_shader(shader, "TRIS", {'pos': points}, indices=indices)
    for z in range(-5,5):
        gpu_hashes = []
        with offscreen.bind():
            shader.uniform_int('z', z)
            shader.uniform_int('screen_size', screen_size)
            batch.draw(shader)
            # Starting from blender 3.0 we can:
            #   fb = gpu.state.active_framebuffer_get()
            #   buffer = fb.read_color(0,0, screen_size, screen_size, 4, 0, UBYTE)
            buffer = bgl.Buffer(bgl.GL_BYTE, screen_size * screen_size * 4)
            bgl.glReadPixels(0, 0, screen_size, screen_size, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)
            x = buffer[:]
            gpu_hashes = [a+256*(b+256*(c+256*d)) for a, b, c, d in zip(x[::4], x[1::4], x[2::4], x[3::4])]
        i = 0
        for y in range(-screen_size//2, screen_size//2):
            for x in range(-screen_size//2, screen_size//2):
                cpu_hash = cpu_func(grid, [x, y, z])
                assert gpu_hashes[i] == cpu_hash
                i += 1


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_gpu_similarity_bucket():
    perform_gpu_test(bucket_frag, accel.HashedGrid.hash_grid)

def cpu_dot_5_offset_func(grid, xyz):
    return grid.hash_coord([i+0.5 for i in xyz])

@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_gpu_similarity_coords():
    perform_gpu_test(coord_frag, cpu_dot_5_offset_func)


def test_build():
    grid = accel.HashedGrid(1)
    points = np.array([[x/10, 0, 0] for x in range(500)], dtype=numpyutils.float32_dtype)
    grid.build(points)
