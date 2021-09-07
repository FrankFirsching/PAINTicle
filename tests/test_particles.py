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

import time

import painticle
from painticle.sim import particle_simulator

from . import tstutils


class SetupInfo(object):
    def __init__(self, tst_mesh, context, particles, delta_t, settings, event):
        self.tst_mesh = tst_mesh
        self.context = context
        self.particles = particles
        self.delta_t = delta_t
        self.settings = settings
        self.event = event


def sim_only(setup_info):
    interaction = particle_simulator.Interactions.EMIT_PARTICLES
    setup_info.particles.start_interacting(setup_info.context, setup_info.event, interaction)
    for i in range(100):
        setup_info.particles.interact(setup_info.context, setup_info.event, interaction)
        setup_info.particles.move_particles(setup_info.delta_t, setup_info.settings)


def sim_and_paint(setup_info):
    interaction = particle_simulator.Interactions.EMIT_PARTICLES
    setup_info.particles.start_interacting(setup_info.context, setup_info.event, interaction)
    for i in range(100):
        setup_info.particles.interact(setup_info.context, setup_info.event, interaction)
        setup_info.particles.move_particles(setup_info.delta_t, setup_info.settings)
        setup_info.particles.paint_particles(setup_info.delta_t)


@pytest.fixture
def sim_setup():
    tstutils.open_file("benchmark_particles.blend")
    bpy.ops.object.mode_set(mode="TEXTURE_PAINT")
    test_mesh = bpy.data.objects['test_object']
    context = tstutils.get_default_context(test_mesh)
    painticle_settings = bpy.context.scene.painticle_settings
    particles = painticle.particles.Particles(context, omit_painter=tstutils.no_ui())
    return SetupInfo(test_mesh, context, particles, 0.01, painticle_settings,
                     tstutils.get_fake_event(x=context.region.width//2, y=context.region.height//2))


def test_benchmark_no_painting_sim(benchmark, sim_setup):
    benchmark.pedantic(sim_only, args=(sim_setup,), rounds=1)


@pytest.mark.skipif(tstutils.no_ui(), reason="requires UI")
def test_benchmark_painting_sim(benchmark, sim_setup):
    benchmark.pedantic(sim_and_paint, args=(sim_setup,), rounds=1)
