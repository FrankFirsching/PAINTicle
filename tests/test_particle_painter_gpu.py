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
import mathutils

from painticle import particle
from painticle import particle_painter_gpu
from painticle import settings

import tstutils
from tstutils import default_scene


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_particle_visual_attribs(default_scene):
    particle_settings = bpy.context.scene.painticle_settings
    p = particle.Particle(mathutils.Vector(), 0, mathutils.Color((0.3, 0.4, 0.5)), None, particle_settings)
    assert p
    visual_attribs = []
    painter = particle_painter_gpu.ParticlePainterGPU(tstutils.get_default_context())
    painter.append_visual_properties(visual_attribs, p)
    assert visual_attribs[0] == p.location[0]
    assert visual_attribs[1] == p.location[1]
    assert visual_attribs[2] == p.location[2]
    assert visual_attribs[3] == p.uv[0]
    assert visual_attribs[4] == p.uv[1]
    assert visual_attribs[5] == p.particle_size
    assert visual_attribs[6] == p.age
    assert visual_attribs[7] == p.max_age
    assert visual_attribs[8] == p.color.r
    assert visual_attribs[9] == p.color.g
    assert visual_attribs[10] == p.color.b
