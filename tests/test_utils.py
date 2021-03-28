import pytest

import mathutils

from particle_paint import utils

import tstutils

def test_lerp():
    assert tstutils.is_close(utils.lerp(0.3,1,2), 1.3, 1e-4)

def test_matrix_to_tuple():
    m = mathutils.Matrix()
    # Check identity matrix
    assert utils.matrix_to_tuple(m) == (1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
    # Translation matrix
    m = mathutils.Matrix.Translation(mathutils.Vector((1,2,3)))
    assert utils.matrix_to_tuple(m) == (1,0,0,0, 0,1,0,0, 0,0,1,0, 1,2,3,1)
