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

# Testing the particle shader

# <pep8 compliant>

import pytest

from painticle import gpu_utils

from . import tstutils


@pytest.mark.skipif(tstutils.no_validator(), reason="requires GLSL validator")
def test_glsl_validation():
    vert, frag, geom = gpu_utils.load_shader_source("texture_preview", ["utils"])
    assert gpu_utils.validate_glsl_shaders(vert, "vert")
    assert gpu_utils.validate_glsl_shaders(frag, "frag")
    assert gpu_utils.validate_glsl_shaders(geom, "geom")
