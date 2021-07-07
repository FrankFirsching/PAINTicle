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

import bpy

from painticle import particle_painter_gpu

from . import tstutils
from .tstutils import default_scene


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_painter_creation(default_scene):
    painter = particle_painter_gpu.ParticlePainterGPU(tstutils.get_default_context())
    assert painter is not None
