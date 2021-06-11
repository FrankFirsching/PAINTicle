#!/usr/bin/python

import os
import sys
import re
import shutil
import subprocess

# Default configuration
default_dependencies = ("embree", "tbb", "python")


def call(cmd, exit_on_error=True, silent=False):
    if not silent:
        print(" ".join(cmd))

    # Flush to ensure correct order output on Windows.
    sys.stdout.flush()
    sys.stderr.flush()

    completed = subprocess.run(cmd, capture_output=True, text=True)
    if not silent:
        print(completed.stdout)
        print(completed.stderr)
    completed.check_returncode()
    return completed


def dependencies_path():
    script_path = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(script_path, "..", "build", "dependencies")


def download_dependencies(blender_release, dependencies=None, clean=False):
    if dependencies is None:
        dependencies = default_dependencies
    svn_platform = None
    if sys.platform == "win32":
        svn_platform = "win64_vc15"
    elif sys.platform == "linux":
        svn_platform = "linux_centos7_x86_64"
    else:
        raise RuntimeError("Unknown platform"+str(sys.platform))

    # Downloading
    svn_repo_url = "https://svn.blender.org/svnroot/bf-blender/tags/blender-"+blender_release+"-release/lib/"+svn_platform
    deps_path = dependencies_path()
    if os.path.exists(deps_path) and clean:
        shutil.rmtree(deps_path)

    if not os.path.exists(deps_path):
        os.makedirs(deps_path)
    for dependency in dependencies:
        print("Installing dependency", dependency)
        cmd = ["svn", "--non-interactive", "checkout", svn_repo_url+"/"+dependency,
               os.path.join(deps_path, dependency)]
        call(cmd)


def get_downloaded_blender_version():
    cmd = ["svn", "info", os.path.join(dependencies_path(), "python")]
    result = call(cmd, silent=True)
    regex = re.compile("URL: https://svn.blender.org/svnroot/bf-blender/tags/blender-(.*)-release/lib/")
    found = regex.findall(result.stdout)
    return found[0]


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Dependencies downloader.')
    parser.add_argument('blender_release', help="Blender version")
    parser.add_argument('--clean', help="Clean before downloading", action="store_true")
    args = parser.parse_args()
    download_dependencies(args.blender_release, clean=args.clean)
