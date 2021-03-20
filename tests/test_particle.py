import pytest

import bpy
import mathutils

from particle_paint import particle
from particle_paint import settings

import tstutils


def is_close(v1, v2, tolerance):
    return  (v1 >= v2 - tolerance) and (v1 <= v2 + tolerance)


def test_particle():
    particle_settings = bpy.context.scene.particle_paint_settings
    #tstutils.wait_for_debugger_attached()
    p = particle.Particle(mathutils.Vector(), 0, mathutils.Color((0.3, 0.4, 0.5)), None, particle_settings)
    assert p
    visual_attribs = []
    p.append_visual_properties(visual_attribs)
    assert visual_attribs[0] == p.uv[0]
    assert visual_attribs[1] == p.uv[1]
    assert visual_attribs[2] == p.particle_size
    assert visual_attribs[3] == p.age
    assert visual_attribs[4] == p.max_age
    assert visual_attribs[5] == p.color.r
    assert visual_attribs[6] == p.color.g
    assert visual_attribs[7] == p.color.b
