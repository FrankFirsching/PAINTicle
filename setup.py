from numpy import lib
from setuptools import setup, Extension
import platform
import os
import sys
import glob
import re

from scripts import download_blender_dependencies
blender_version = download_blender_dependencies.get_downloaded_blender_version()


def setup_compiler_dirs(dependencies, bost_modules=None):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dependencies_dir = os.path.join(script_dir, "build", "dependencies")
    include_dirs = []
    library_dirs = []
    libraries = []
    for dep in dependencies:
        pkg_dir = os.path.join(dependencies_dir, dep)
        include_dir = os.path.join(pkg_dir, "include")
        library_dir = os.path.join(pkg_dir, "lib")
        if dep == "python":
            if blender_version == "2.92":
                include_dir = os.path.join(include_dir, "python3.7m")
            else:
                include_dir = os.path.join(include_dir, "python3.9")
        if os.path.exists(include_dir):
            include_dirs.append(include_dir)
        if os.path.exists(library_dir):
            library_dirs.append(library_dir)
            for file in glob.glob(os.path.join(library_dir, '*')):
                if os.path.isfile(file):
                    lib_file = os.path.basename(file)
                    lib_file = os.path.splitext(lib_file)[0]
                    lib_file = lib_file.replace("lib", "")
                    if dep != "boost" or lib_file in bost_modules:
                        libraries.append(lib_file)
    if sys.platform == "win32":
        # We need some fixed libs on Windows
        libraries.extend(["advapi32", "psapi"])
    return include_dirs, library_dirs, libraries


def get_addon_version():
    """ Parse blender's bl_info structure defined in the addon's __init__.py to get the version """
    version_expr = re.compile('"version"\\s*:\\s*\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\)')
    with open("painticle/__init__.py") as fp:
        lines = fp.readlines()
        for line in lines:
            match = version_expr.search(line)
            if match is not None:
                return match[1]+"."+match[2]+"."+match[3]
    # Fallback, if no version information in addon
    return "0.0.1"


# Combined
include_dirs, library_dirs, libraries = setup_compiler_dirs(["embree", "tbb", "python", "pybind11"], [])

if sys.platform == "linux":
    # Linux linker normally needs --start-group ... --end-group flags, but we can't configure the setuptools command
    # line that precisely. So we just add all found libraries twice to sort out interdependencies of the libs
    libraries += libraries


def setup_package():
    undef_macros = []
    if "--debug" in sys.argv:
        undef_macros = ["NDEBUG"]
    if platform.system() == 'Windows':
        macros = []
    elif platform.system() == 'Linux':
        macros = [("_GLIBCXX_USE_CXX11_ABI", 0)]

    native_module = Extension('painticle.bvh',
                              define_macros=macros,
                              undef_macros=undef_macros,
                              include_dirs=include_dirs,
                              library_dirs=library_dirs,
                              libraries=libraries+libraries,
                              sources=glob.glob('painticle/bvh/*.cpp'),
                              depends=glob.glob('painticle/bvh/*.h'))

    setup(name='painticle',
          version=get_addon_version(),
          description='The blender PAINTicle addon',
          packages=['painticle'],
          ext_modules=[native_module],
          package_data={
            "painticle": ["shaders/*.glsl", "dependencies.txt"]
          },
          exclude_package_data={
              "painticle": ["bvh/*"]
          },
          include_package_data=True)


if __name__ == '__main__':
    setup_package()
