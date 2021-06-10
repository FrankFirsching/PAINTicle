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
import numpy as np
import bpy

from painticle import numpyutils

from . import tstutils

min_tol = 0.000001

vec3_dtype = np.dtype([('x', np.single), ('y', np.single), ('z', np.single)], align=True)
struct_dtype = np.dtype([('a', vec3_dtype),
                         ('b', vec3_dtype),
                         ('c', np.single)],
                          align=True)


def test_repeated_vec():
    vec = (1, 2, 3)
    n = 4
    x = numpyutils.repeated_vec(vec, n, dtype=vec3_dtype)
    assert x.size == n
    for i in range(x.size):
        assert tstutils.is_close_vec(x[i], (1, 2, 3), min_tol), f"on element i={i}"


def test_length():
    vec = (1, 2, 2)
    n = 1000
    x = numpyutils.repeated_vec(vec, n, dtype=vec3_dtype)
    y = numpyutils.vec_length(x)
    assert x.size == n
    for i in range(x.size):
        assert y[i] == 3, f"on element i={i}"
