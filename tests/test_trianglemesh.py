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

# Testing the triangle mesh class

import pytest
import bpy
import mathutils    

from painticle import trianglemesh

import tstutils

@pytest.fixture
def test_mesh():
    tstutils.open_file("trianglemesh_test.blend")
    blendobject = bpy.data.objects['test_object']
    return trianglemesh.TriangleMesh(blendobject)


def test_construction(test_mesh):
    assert test_mesh is not None
    # testing, that the face we're working with during other tests is at the right expected location
    tri = test_mesh.mesh.loop_triangles[2]
    tri_p = [test_mesh.mesh.vertices[i].co  for i in tri.vertices]
    assert tri_p[0] == mathutils.Vector((1.0, -1.0, -1.0))
    assert tri_p[1] == mathutils.Vector((1.0, -1.0, 1.0))
    assert tri_p[2] == mathutils.Vector((-1.0, -1.0, 1.0))


def test_triangle_for_point_on_poly(test_mesh):
    p = mathutils.Vector((0.2, 0.7, 1))
    assert test_mesh.triangle_for_point_on_poly(p, 0) == 0
    p = mathutils.Vector((0.7, 0.2, 1))
    assert test_mesh.triangle_for_point_on_poly(p, 0) == 1
    p = mathutils.Vector((1.7, 1.7, 1))
    assert test_mesh.triangle_for_point_on_poly(p, 0) is None


def test_project_point_to_triangle(test_mesh):
    p = mathutils.Vector((0.2, 0.7, 1.4))
    p_proj = test_mesh.project_point_to_triangle(p, 0)
    assert p_proj == mathutils.Vector((0.2, 0.7, 1))


def test_move_over_triangle_boundaries(test_mesh):
    p0 = mathutils.Vector((0.2, 0.7, 1))
    p1 = mathutils.Vector((0.7, 0.2, 1.1))
    p_new, tri_new, was_moved = test_mesh.move_over_triangle_boundaries(p0, p1, 0)
    assert was_moved is True
    assert tri_new == 1
    assert p_new == mathutils.Vector((0.7, 0.2, 1))


def test_mappings(test_mesh):
    assert len(test_mesh.poly_to_tri) == 6
    assert len(test_mesh.tri_to_poly) == 12


def test_barycentrics(test_mesh):
    p = mathutils.Vector((0.2, -1.0, 0.6))
    test_bary = test_mesh.barycentrics(p, 2)
    assert all([test_bary[i] > 0 for i in range(3)])
    assert test_bary[0]+test_bary[1]+test_bary[2] == 1


def test_edge_start_end(test_mesh):
    assert test_mesh.edgeStart(0) == 0
    assert test_mesh.edgeEnd(0) == 4
