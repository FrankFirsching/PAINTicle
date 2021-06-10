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

import numpy as np

from painticle import bvh

from . import tstutils

min_tol = 0.000001


def test_bvh_closest_point():
    points = np.array([-1, -1, 0,
                       +1, -1, 0,
                       +1, +1, 0,
                       -1, +1, 0], dtype=np.single)
    triangles = np.array([0, 1, 2,    0, 2, 3], dtype=np.uintc)
    normals = np.array([], dtype=np.single)

    x = bvh.build_bvh(points, triangles, normals)
    surface_info = x.closest_point(0.1, 0.7, 1)
    assert tstutils.is_close_vec(surface_info.barycentrics, [0.15, 0.55, 0.3], min_tol)
    assert tstutils.is_close_vec(surface_info.location, [0.1, 0.7, 0], min_tol)
    assert surface_info.tri_index == 1

    surface_info = x.closest_point(0.1, 0.7, -1)
    assert tstutils.is_close_vec(surface_info.location, [0.1, 0.7, 0], min_tol)
    assert tstutils.is_close_vec(surface_info.barycentrics, [0.15, 0.55, 0.3], min_tol)
    assert surface_info.tri_index == 1

    surface_info = x.closest_point(1.1, 0.7, 0)
    assert tstutils.is_close_vec(surface_info.location, [1.0, 0.7, 0], min_tol)
    assert tstutils.is_close_vec(surface_info.barycentrics, [0, 0.15, 0.85], min_tol)
    assert surface_info.tri_index == 0

    surface_info = x.closest_point(-1.1, 0.7, 0)
    assert tstutils.is_close_vec(surface_info.location, [-1.0, 0.7, 0], min_tol)
    assert tstutils.is_close_vec(surface_info.barycentrics, [0.15, 0, 0.85], min_tol)
    assert surface_info.tri_index == 1

    surface_info = x.closest_point(0.5, 0.5, 0)
    assert tstutils.is_close_vec(surface_info.location, [0.5, 0.5, 0], min_tol)
    assert tstutils.is_close_vec(surface_info.barycentrics, [0.25, 0, 0.75], min_tol)
    assert surface_info.tri_index == 0


def test_bvh_normal_interpolation():
    points = np.array([-1, -1, 0,
                       +1, -1, 0,
                       +1, +1, 0,
                       -1, +1, 0], dtype=np.single)
    triangles = np.array([0, 1, 2,    0, 2, 3], dtype=np.uintc)
    normals = np.array([1, 2, 0,
                        2, 3, 0,
                        3, 4, 0,
                        4, 5, 0,
                        5, 6, 0,
                        6, 7, 0], dtype=np.single)

    x = bvh.build_bvh(points, triangles, normals)
    surface_info = x.closest_point(0.1, 0.7, 1)
    assert surface_info.tri_index == 1
    assert tstutils.is_close_vec(surface_info.barycentrics, [0.15, 0.55, 0.3], min_tol)
    assert tstutils.is_close_vec(surface_info.location, [0.1, 0.7, 0], min_tol)
    assert tstutils.is_close_vec(surface_info.normal, [5.15, 6.15, 0.0], min_tol)


def test_bvh_intersection():
    points = np.array([-1, -1, 0,
                       +1, -1, 0,
                       +1, +1, 0,
                       -1, +1, 0], dtype=np.single)
    triangles = np.array([0, 1, 2,    0, 2, 3], dtype=np.uintc)
    normals = np.array([1, 2, 0,
                        2, 3, 0,
                        3, 4, 0,
                        4, 5, 0,
                        5, 6, 0,
                        6, 7, 0], dtype=np.single)

    x = bvh.build_bvh(points, triangles, normals)
    surface_info = x.shoot_ray([0.1, 0, 0.7], [0, 1, -1])
    assert surface_info.tri_index == 1
    assert tstutils.is_close_vec(surface_info.barycentrics, [0.15, 0.55, 0.3], min_tol)
    assert tstutils.is_close_vec(surface_info.location, [0.1, 0.7, 0], min_tol)
    assert tstutils.is_close_vec(surface_info.normal, [5.15, 6.15, 0.0], min_tol)