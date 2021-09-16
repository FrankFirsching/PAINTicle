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
import numpy as np

from . import tstutils

from painticle.ops.createdefaultbrushtree import create_default_brush_tree
from painticle.sim import particle_simulator, particle_simulator_cpu
from painticle import trianglemesh
from painticle import numpyutils

min_tol = 1e-6


@pytest.fixture
def test_mesh():
    tstutils.open_file("particle_test.blend")
    return bpy.data.objects['test_object']


def test_particle_creation(test_mesh):
    global min_tol
    context = tstutils.get_default_context()
    paint_mesh = trianglemesh.TriangleMesh(context)
    simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
    create_default_brush_tree()
    simulator.setup_steps()
    emit_settings = simulator.emit_settings()
    emit_settings.color_random = (0,0,0)
    painticle_settings = context.scene.painticle_settings
    # Add one particle
    simulator.add_test_particles(np.array([(2, 0.2, 0.3)], dtype=numpyutils.float32_dtype),
                                 np.array([(-1, 0, 0)], dtype=numpyutils.float32_dtype),
                                 paint_mesh.bvh, mathutils.Matrix.Identity(4), (0.1, 0.2, 0.3), painticle_settings)
    p = simulator._particles
    assert p is not None
    assert p.num_particles == 1
    assert tstutils.is_close_vec(p.location[0], (1, 0.2, 0.3), min_tol)
    assert tstutils.is_close_vec(p.acceleration[0], (0, 0, 0), min_tol)
    assert tstutils.is_close_vec(p.speed[0], (0, 0, 0), min_tol)
    assert tstutils.is_close_vec(p.normal[0], (1, 0, 0), min_tol)
    assert tstutils.is_close_vec(p.uv[0], (0, 0), min_tol)
    assert tstutils.is_close(p.size[0], emit_settings.particle_size, emit_settings.particle_size_random)
    assert tstutils.is_close(p.mass[0], emit_settings.mass, emit_settings.mass_random)
    assert tstutils.is_close(p.age[0], 0, min_tol)
    assert tstutils.is_close(p.max_age[0], emit_settings.max_age, emit_settings.max_age_random)
    assert tstutils.is_close_vec(p.color[0], (0.1, 0.2, 0.3), min_tol)
    # Add another particle
    simulator.add_test_particles(np.array([(0.3, 0.4, 2)], dtype=numpyutils.float32_dtype),
                                 np.array([(0, 0, -1)], dtype=numpyutils.float32_dtype),
                                 paint_mesh.bvh, mathutils.Matrix.Identity(4), (0.1, 0.2, 0.3), painticle_settings)
    p = simulator._particles
    assert p is not None
    assert p.num_particles == 2


def test_particle_simulation(test_mesh):
    global min_tol
    context = tstutils.get_default_context(test_mesh)
    paint_mesh = trianglemesh.TriangleMesh(context)
    simulator = particle_simulator_cpu.ParticleSimulatorCPU(context)
    create_default_brush_tree()
    simulator.setup_steps()
    painticle_settings = context.scene.painticle_settings
    emit_settings = simulator.emit_settings()
    emit_settings.particle_size_random = 0
    emit_settings.mass_random = 0
    emit_settings.max_age_random = 0
    simulator.add_test_particles(np.array([(2, 0.2, 0.3)], dtype=numpyutils.float32_dtype),
                                 np.array([(-1, 0, 0)], dtype=numpyutils.float32_dtype),
                                 paint_mesh.bvh, mathutils.Matrix.Identity(4), (0.1, 0.2, 0.3), painticle_settings)
    input = particle_simulator.SourceInput()
    emit_settings = simulator.emit_settings()
    sim_data = particle_simulator.SimulationData(0.1, emit_settings, painticle_settings, paint_mesh, context, input)
    simulator.simulate(sim_data)
    assert tstutils.is_close_vec(simulator._particles.location[0], (1, 0.2, 0.26457503), min_tol)
    assert tstutils.is_close(simulator._particles.age[0], sim_data.timestep, min_tol)
