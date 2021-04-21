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

# Dependency utilities

import importlib
import os
import pkg_resources
import sys
import site
import subprocess
import bpy

# A private variable to store the list of requested dependencies
_dependencies = None


def install_all():
    total = len(_dependencies)
    wm = bpy.context.window_manager
    if wm is not None:
        wm.progress_begin(0, total)
    need_reload = False
    try:
        for i, requirement in enumerate(_dependencies):
            if not is_dependency_installed(requirement.name):
                if _install_requirement(requirement):
                    need_reload = True
            if wm is not None:
                wm.progress_update(i)
    finally:
        if wm is not None:
            wm.progress_end()
    if need_reload:
        importlib.invalidate_caches()


def is_dependency_installed(module_name):
    """ Check for a single dependency """
    return importlib.util.find_spec(module_name) is not None


def are_dependencies_installed():
    """ Check, if all dependencies are available """
    for module in _dependencies:
        if not is_dependency_installed(module.name):
            return False
    return True


def load_dependency(module):
    try:
        return importlib.import_module(module)
    except ImportError:
        return None


def _setup(dependencies):
    global _dependencies
    if _dependencies != dependencies and _dependencies is not None:
        raise RuntimeError("dependencies.setup(...) called twice with different dependencies list.")
    if dependencies is None:
        raise RuntimeError("dependencies.setup(...) called with None.")
    _dependencies = dependencies
    _ensure_local_site_packages()


def _ensure_local_site_packages():
    """ We need to activate the usage of local site packages. """
    if site.USER_SITE not in sys.path:
        sys.path.append(site.USER_SITE)


def _install_requirement(requirement):
    """ Install a python module through pip """
    completed_process = subprocess.run([sys.executable, "-m", "pip", "install", str(requirement), "--user"])
    return completed_process.returncode == 0


def _are_dependencies_installed(self):
    """ Wrapper for the preferences panel callback """
    return are_dependencies_installed()


def _on_install_dependencies(self, value):
    """ A wrapper for the preferences panel callback """
    if value:
        install_all()
        bpy.ops.script.reload()


def DependenciesProperty():
    """ A helper property to facilitate an install dependencies button in the preferences """
    return bpy.props.BoolProperty(name="Install dependencies",
                                  description="Activate to ensure, that the needed dependencies are installed",
                                  set=_on_install_dependencies,
                                  get=_are_dependencies_installed)


def draw_property(panel, name):
    row = panel.layout.row()
    row.label(text='Dependencies:')
    row.prop(panel, name, toggle=1)


if _dependencies is None:
    dependencies_file = os.path.join(os.path.dirname(__file__), "dependencies.txt")
    with open(dependencies_file) as f:
        lines = f.readlines()
        deps = [pkg_resources.Requirement(line) for line in lines if line.rstrip() != '']
        _setup(deps)
        install_all()
