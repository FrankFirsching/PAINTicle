import pytest
import bpy
import mathutils    

from particle_paint import gpu_utils

import tstutils

@pytest.fixture
def test_mesh():
    tstutils.open_file("textures_test.blend")
    return bpy.data.objects['test_object']

def test_texture_size_non_tiled(test_mesh):
    assert test_mesh is not None
    image = test_mesh.active_material.node_tree.nodes['myUntiledImage'].image
    image_sizes = gpu_utils.image_sizes(image)
    assert len(image_sizes) == 1
    assert image_sizes[0][:] == (1024,512)

    image_size = gpu_utils.max_image_size(image)
    assert image_size[:] == (1024,512)

# blender currently doesn't allow scripting for UDIM images. It just doesn't provide enough data for the tiles.
@pytest.mark.xfail
def test_texture_size_udim(test_mesh):
    assert test_mesh is not None
    image = test_mesh.active_material.node_tree.nodes['myUDIM'].image
    image_sizes = gpu_utils.image_sizes(image)
    assert len(image_sizes) == 2
    assert image_sizes[0][:] == (1024,512)
    assert image_sizes[1][:] == (256,1024)


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_offscreen_creation_from_image(test_mesh):
    image = test_mesh.active_material.node_tree.nodes['myUntiledImage'].image
    buffer = gpu_utils.gpu_buffer_for_image(image)
    assert buffer.width == 1024
    assert buffer.height == 512
