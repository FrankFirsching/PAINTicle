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

# Testing the GPU utilities

# <pep8 compliant>

import pytest
import bpy
import moderngl

from painticle import gpu_utils

from . import tstutils


@pytest.fixture
def test_mesh():
    tstutils.open_file("textures_test.blend")
    return bpy.data.objects['test_object']


def test_image_sizes_null_image():
    assert gpu_utils.image_sizes(None) == [(0, 0)]


def test_texture_size_non_tiled(test_mesh):
    assert test_mesh is not None
    image = test_mesh.active_material.node_tree.nodes['myUntiledImage'].image
    image_sizes = gpu_utils.image_sizes(image)
    assert len(image_sizes) == 1
    assert image_sizes[0][:] == (1024, 512)

    image_size = gpu_utils.max_image_size(image)
    assert image_size == (1024, 512)


# blender currently doesn't allow scripting for UDIM images. It just doesn't provide enough data for the tiles.
@pytest.mark.xfail
def test_texture_size_udim(test_mesh):
    assert test_mesh is not None
    image = test_mesh.active_material.node_tree.nodes['myUDIM'].image
    image_sizes = gpu_utils.image_sizes(image)
    assert len(image_sizes) == 2
    assert image_sizes[0][:] == (1024, 512)
    assert image_sizes[1][:] == (256, 1024)


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_offscreen_creation_from_image(test_mesh):
    image = test_mesh.active_material.node_tree.nodes['myUntiledImage'].image
    glcontext = moderngl.create_context()
    buffer = gpu_utils.gpu_framebuffer_for_image(image, glcontext)
    assert buffer.width == 1024
    assert buffer.height == 512
