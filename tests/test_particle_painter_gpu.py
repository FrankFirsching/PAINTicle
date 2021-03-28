import pytest

import bpy
import mathutils

from particle_paint import particle
from particle_paint import particle_painter_gpu
from particle_paint import settings

import tstutils


def test_particle():
    particle_settings = bpy.context.scene.particle_paint_settings
    p = particle.Particle(mathutils.Vector(), 0, mathutils.Color((0.3, 0.4, 0.5)), None, particle_settings)
    assert p
    visual_attribs = []
    painter = particle_painter_gpu.ParticlePainterGPU(bpy.context)
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
