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
    wm.progress_begin(0, total)
    try:
        for i, requirement in enumerate(_dependencies):
            if not is_dependency_installed(requirement.name):
                _install_requirement(requirement)
            wm.progress_update(i)
    finally:
        wm.progress_end()


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
    subprocess.run([sys.executable, "-m", "pip", "install", str(requirement), "--user"])


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
    panel.layout.label(text='Dependencies')
    row = panel.layout.row()
    row.prop(panel, name, toggle=1)


if _dependencies is None:
    dependencies_file = os.path.join(os.path.dirname(__file__), "dependencies.txt")
    with open(dependencies_file) as f:
        lines = f.readlines()
        deps = [pkg_resources.Requirement(line) for line in lines if line.rstrip() != '']
        _setup(deps)
        install_all()
