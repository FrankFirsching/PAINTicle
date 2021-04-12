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
import types

from painticle import dependencies

import tstutils


def test_is_available():
    # All dependencies should already be installed by importing dependencies
    assert dependencies.is_dependency_installed("moderngl") is True
    assert dependencies.are_dependencies_installed() is True
    assert dependencies.load_dependency("moderngl") is not None


def test_import():
    import moderngl
    assert isinstance(moderngl, types.ModuleType)
