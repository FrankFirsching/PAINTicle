# Testing the particle shader

# <pep8 compliant>

import pytest
import types

from particle_paint import dependencies

import tstutils


def test_is_available():
    # All dependencies should already be installed by importing dependencies
    assert dependencies.is_dependency_installed("moderngl") is True
    assert dependencies.are_dependencies_installed() is True
    assert dependencies.load_dependency("moderngl") is not None


def test_import():
    import moderngl
    assert isinstance(moderngl, types.ModuleType)
