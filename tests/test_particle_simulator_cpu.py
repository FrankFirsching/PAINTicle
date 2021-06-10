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
import numpy as np

from . import tstutils

from painticle import particle_simulator, trianglemesh
from painticle import particle_simulator_cpu


min_tol = 1e-6


@pytest.fixture
def test_mesh():
    tstutils.open_file("particle_test.blend")
    return bpy.data.objects['test_object']

def test_particle_simulator():
    context = tstutils.get_default_context()
    simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
    assert simulator is not None
    assert simulator.num_particles == 0
    new_particle = np.zeros(1, particle_simulator_cpu.particle_dtype)
    simulator.add_particles(new_particle)
    assert simulator.num_particles == 1
    simulator.shutdown()


def test_particle_creation():
    global min_tol
    context = tstutils.get_default_context()
    simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
    painticle_settings = context.scene.painticle_settings
    p = simulator.create_particle((1, 2, 3), (0.1, 0.2, 0.3), (4, 5, 6), painticle_settings)
    assert p is not None
    assert tstutils.is_close_vec(p['location'][0], (1, 2, 3), min_tol)
    assert tstutils.is_close_vec(p['acceleration'][0], (0, 0, 0), min_tol)
    assert tstutils.is_close_vec(p['speed'][0], (4, 5, 6), min_tol)
    assert tstutils.is_close_vec(p['normal'][0], (0, 0, 0), min_tol)
    assert tstutils.is_close_vec(p['uv'][0], (0, 0), min_tol)
    assert tstutils.is_close(p['size'][0], painticle_settings.particle_size, painticle_settings.particle_size_random)
    assert tstutils.is_close(p['mass'][0], painticle_settings.mass, painticle_settings.mass_random)
    assert tstutils.is_close(p['age'][0], 0, min_tol)
    assert tstutils.is_close(p['max_age'][0], painticle_settings.max_age, painticle_settings.max_age_random)
    assert tstutils.is_close_vec(p['color'][0], (0.1, 0.2, 0.3), min_tol)


def test_particle_addition():
    context = tstutils.get_default_context()
    simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
    painticle_settings = context.scene.painticle_settings
    p = simulator.create_particle((1, 2, 3), (0.1, 0.2, 0.3), (4, 5, 6), painticle_settings)
    assert p is not None
    simulator.add_particles([p])
    assert simulator.num_particles == 1


def test_particle_simulation(test_mesh):
    global min_tol
    context = tstutils.get_default_context(test_mesh)
    paint_mesh = trianglemesh.TriangleMesh(context)
    simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
    painticle_settings = context.scene.painticle_settings
    painticle_settings.particle_size_random = 0
    painticle_settings.mass_random = 0
    painticle_settings.max_age_random = 0
    p = simulator.create_particle((0, 0, 0), (0.1, 0.2, 0.3), (0, 0, 0), painticle_settings)
    simulator.add_particles([p])
    sim_data = particle_simulator.SimulationData(1, painticle_settings, paint_mesh, None)
    simulator.simulate(sim_data)
    assert tstutils.is_close_vec(simulator._particles['location'][0], (0, 0, -1), min_tol)
    assert tstutils.is_close(simulator._particles['age'][0], sim_data.timestep, min_tol)
