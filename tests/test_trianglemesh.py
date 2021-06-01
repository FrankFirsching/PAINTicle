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
    assert test_object.bvh is not None
