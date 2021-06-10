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

# Testing the a single particle

# <pep8 compliant>

import pytest
import bpy
import mathutils
import sys

from painticle import particle
from painticle import trianglemesh

from . import tstutils


@pytest.fixture
def test_mesh():
    tstutils.open_file("particle_test.blend")
    return bpy.data.objects['test_object']


def test_particle(test_mesh):
    particle_settings = bpy.context.scene.painticle_settings
    loc = mathutils.Vector((0.2, 0.7, 1))
    tri_index = 0
    color = mathutils.Color((0.5, 0.6, 0.7))
    null_vec3 = mathutils.Vector((0, 0, 0))
    z_axis = mathutils.Vector((0, 0, 1))

    assert test_mesh is not None
    context = tstutils.get_default_context(test_mesh)
    paint_mesh = trianglemesh.TriangleMesh(context)

    p = particle.Particle(loc, color, paint_mesh, particle_settings)
    assert p
    min_tol = 0.000001
    assert tstutils.is_close_vec(p.location, loc, min_tol)
    assert p.acceleration == null_vec3
    assert p.speed == null_vec3
    assert p.normal == z_axis
    assert p.uv == mathutils.Vector((0.725, 0.5375))
    assert tstutils.is_close(p.particle_size, particle_settings.particle_size, particle_settings.particle_size_random)
    assert tstutils.is_close(p.mass, particle_settings.mass, particle_settings.mass_random)
    assert p.age == 0
    assert tstutils.is_close(p.max_age, particle_settings.max_age, particle_settings.max_age_random)
    # color randomness is by default 0, so we need a certain epsilon as the tolerance
    assert tstutils.is_close(p.color.h, color.h, max(particle_settings.color_random.h, min_tol))
    assert tstutils.is_close(p.color.s, color.s, max(particle_settings.color_random.s, min_tol))
    assert tstutils.is_close(p.color.v, color.v, max(particle_settings.color_random.v, min_tol))

    p_next = particle.Particle(loc, color, None, particle_settings)
    assert p.id != p_next.id
