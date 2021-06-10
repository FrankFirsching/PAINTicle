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

# Testing PAINTicle's utilities

import pytest

import mathutils

from painticle import utils

from . import tstutils


def test_lerp():
    assert tstutils.is_close(utils.lerp(0.3, 1, 2), 1.3, 1e-4)


def test_matrix_to_tuple():
    m = mathutils.Matrix()
    # Check identity matrix
    assert utils.matrix_to_tuple(m) == (1, 0, 0, 0,
                                        0, 1, 0, 0,
                                        0, 0, 1, 0,
                                        0, 0, 0, 1)
    # Translation matrix
    m = mathutils.Matrix.Translation(mathutils.Vector((1, 2, 3)))
    assert utils.matrix_to_tuple(m) == (1, 0, 0, 0,
                                        0, 1, 0, 0,
                                        0, 0, 1, 0,
                                        1, 2, 3, 1)
