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

# Testing the triangle mesh class

import pytest
import bpy
import mathutils

from painticle import trianglemesh

import tstutils


def get_triangle_mesh(blend_object_name):
    blendobject = bpy.data.objects[blend_object_name]
    context = tstutils.get_default_context(blendobject)
    return trianglemesh.TriangleMesh(context)


@pytest.fixture
def test_scene():
    tstutils.open_file('trianglemesh_test.blend')


@pytest.fixture
def test_cube(test_scene):
    return get_triangle_mesh('test_cube')


@pytest.fixture
def test_plane(test_scene):
    return get_triangle_mesh('test_plane')


@pytest.fixture(params=["test_cube", "test_plane", "test_nonmanifold"])
def test_object(request, test_scene):
    """ A fixture, that calls the testcase for each test object in our test scene """
    return get_triangle_mesh(request.param)


def test_construction(test_object):
    # test we're not raising any exception for any of our test geometries
    # including non-manifold meshes
    assert test_object is not None


def test_cube_triangle_2(test_cube):
    assert test_cube is not None
    # testing, that the face we're working with during other tests is at the right expected location
    tri = test_cube.mesh.loop_triangles[2]
    tri_p = [test_cube.mesh.vertices[i].co for i in tri.vertices]
    assert tri_p[0] == mathutils.Vector((1.0, -1.0, -1.0))
    assert tri_p[1] == mathutils.Vector((1.0, -1.0, 1.0))
    assert tri_p[2] == mathutils.Vector((-1.0, -1.0, 1.0))


def test_triangle_for_point_on_poly(test_cube, test_plane):
    # Cube
    p = mathutils.Vector((0.2, 0.7, 1))
    assert test_cube.triangle_for_point_on_poly(p, 0) == 0
    p = mathutils.Vector((0.7, 0.2, 1))
    assert test_cube.triangle_for_point_on_poly(p, 0) == 1
    p = mathutils.Vector((1.7, 1.7, 1))
    assert test_cube.triangle_for_point_on_poly(p, 0) is None
    # Plane
    p = mathutils.Vector((0.2, 0.7, 0))
    assert test_plane.triangle_for_point_on_poly(p, 0) == 1
    p = mathutils.Vector((0.7, 0.2, 0))
    assert test_plane.triangle_for_point_on_poly(p, 0) == 0


def test_mappings(test_cube):
    assert len(test_cube.poly_to_tri) == 6
    assert len(test_cube.tri_to_poly) == 12


def test_barycentrics(test_cube):
    p = mathutils.Vector((0.2, -1.0, 0.6))
    test_bary = test_cube.barycentrics(p, 2)
    assert all([test_bary[i] > 0 for i in range(3)])
    assert test_bary[0]+test_bary[1]+test_bary[2] == 1


def test_edge_start_end(test_cube):
    assert test_cube.edgeStart(0) == 0
    assert test_cube.edgeEnd(0) == 4
