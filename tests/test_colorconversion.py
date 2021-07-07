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
import mathutils


from painticle import accel
from painticle import numpyutils

from . import tstutils

min_tol = 0.000001


rgb_ref = np.array([
        (0.0, 0.0, 0.0),  # black
        (0.0, 0.0, 1.0),  # blue
        (0.0, 1.0, 0.0),  # green
        (0.0, 1.0, 1.0),  # cyan
        (1.0, 0.0, 0.0),  # red
        (1.0, 0.0, 1.0),  # purple
        (1.0, 1.0, 0.0),  # yellow
        (1.0, 1.0, 1.0),  # white
        (0.5, 0.5, 0.5),  # grey
    ], dtype=numpyutils.col_dtype)
hsv_ref = np.array([
            (0.000, 0.0, 0.0),
            (4./6., 1.0, 1.0),
            (2./6., 1.0, 1.0),
            (3./6., 1.0, 1.0),
            (0.000, 1.0, 1.0),
            (5./6., 1.0, 1.0),
            (1./6., 1.0, 1.0),
            (0.000, 0.0, 1.0),
            (0.000, 0.0, 0.5)
    ], dtype=numpyutils.col_dtype)


def test_rgb2hsv():
    hsv = accel.rgb2hsv(rgb_ref)
    for comp, ref in zip(hsv, hsv_ref):
        assert tstutils.is_close_vec(comp, ref, min_tol)


def test_hsv2rgb():
    rgb = accel.hsv2rgb(hsv_ref)
    for comp, ref in zip(rgb, rgb_ref):
        assert tstutils.is_close_vec(comp, ref, min_tol)


rgb_offset_ref = np.array([
            (0.000, 0.000, 0.000),
            (0.180, 0.612, 0.900),
            (0.612, 0.900, 0.180),
            (0.180, 0.900, 0.468),
            (0.900, 0.180, 0.612),
            (0.468, 0.180, 0.900),
            (0.900, 0.468, 0.180),
            (0.900, 0.900, 0.900),
            (0.400, 0.400, 0.400)
    ], dtype=numpyutils.col_dtype)


def test_apply_hsv_offset():
    hsv_offsets = np.array([(-0.1, -0.2, -0.1)]*len(rgb_ref))
    rgb = accel.apply_hsv_offsets(numpyutils.unstructured(rgb_ref), hsv_offsets)
    for comp, ref in zip(rgb, rgb_offset_ref):
        assert tstutils.is_close_vec(comp, ref, min_tol)


rgb_offset_ref_single = np.array([
            (0.50, 0.500, 0.50),
            (0.60, 0.564, 0.54),
            (0.60, 0.552, 0.54),
            (0.60, 0.558, 0.54),
            (0.60, 0.540, 0.54),
            (0.60, 0.570, 0.54),
            (0.60, 0.546, 0.54),
            (0.60, 0.600, 0.60),
            (0.55, 0.550, 0.55)
    ], dtype=numpyutils.col_dtype)


def test_apply_hsv_offset_single():
    hsv_offsets = numpyutils.unstructured(hsv_ref) * 0.1
    rgb_ref_single = mathutils.Color((0.5, 0.5, 0.5))
    rgb = accel.apply_hsv_offsets([rgb_ref_single], hsv_offsets)
    for comp, ref in zip(rgb, rgb_offset_ref_single):
        assert tstutils.is_close_vec(comp, ref, min_tol)
