# Testing the GPU utilities

# <pep8 compliant>

import pytest
import bpy
import mathutils
import sys

from particle_paint import particle
from particle_paint import trianglemesh

import tstutils


@pytest.fixture
def test_mesh():
    tstutils.open_file("particle_test.blend")
    return bpy.data.objects['test_object']


def test_particle(test_mesh):
    particle_settings = bpy.context.scene.particle_paint_settings
    loc = mathutils.Vector((0.2, 0.7, 1))
    tri_index = 0
    color = mathutils.Color((0.5, 0.6, 0.7))
    null_vec3 = mathutils.Vector((0, 0, 0))
    z_axis = mathutils.Vector((0, 0, 1))

    assert test_mesh is not None
    paint_mesh = trianglemesh.TriangleMesh(test_mesh)

    p = particle.Particle(loc, tri_index, color, paint_mesh, particle_settings)
    assert p
    assert p.location == loc
    assert p.tri_index == tri_index
    assert p.acceleration == null_vec3
    assert p.speed == null_vec3
    assert p.barycentric == mathutils.Vector((0.6, 0.25, 0.15))
    assert p.normal == z_axis
    assert p.uv == mathutils.Vector((0.725, 0.5375))
    assert tstutils.is_close(p.particle_size, particle_settings.particle_size, particle_settings.particle_size_random)
    assert tstutils.is_close(p.mass, particle_settings.mass, particle_settings.mass_random)
    assert p.age == 0
    assert tstutils.is_close(p.max_age, particle_settings.max_age, particle_settings.max_age_random)
    # color randomness is by default 0, so we need a certain epsilon as the tolerance
    min_tol = 0.000001
    assert tstutils.is_close(p.color.h, color.h, max(particle_settings.color_random.h, min_tol))
    assert tstutils.is_close(p.color.s, color.s, max(particle_settings.color_random.s, min_tol))
    assert tstutils.is_close(p.color.v, color.v, max(particle_settings.color_random.v, min_tol))

    p_next = particle.Particle(loc, tri_index, color, None, particle_settings)
    assert p.id != p_next.id
