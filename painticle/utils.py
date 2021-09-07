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

# Utility classes

import os

import mathutils


class Error(Exception):
    """ Base class for errors in this module """
    pass


def lerp(t, a, b):
    """ Perform a linear interpolation between a and b using factor t """
    return (1-t)*a + t*b


def matrix_to_tuple(m):
    """ Convert given blender matrix into a tuple to be usable by moderngl """
    return (m[0][0], m[1][0], m[2][0], m[3][0],
            m[0][1], m[1][1], m[2][1], m[3][1],
            m[0][2], m[1][2], m[2][2], m[3][2],
            m[0][3], m[1][3], m[2][3], m[3][3])


def apply_barycentrics(baries, a, b, c):
    return baries[0]*a + baries[1]*b + baries[2]*c


def orthogonalize(x: mathutils.Vector):
    w = x.normalized()
    if abs(w.x) >= abs(w.y):
        # W.x or W.z is the largest magnitude component, swap them
        invLength = 1.0 / w.xz.length
        u = mathutils.Vector((-w.z * invLength, 0.0, w.x * invLength))
    else:
        # W.y or W.z is the largest magnitude component, swap them
        invLength = 1.0 / w.yz.length
        u = mathutils.Vector((0.0, w.z * invLength, -w.y * invLength))
    v = w.cross(u)
    return u, v, w


# We cache the git version, so we don't need to touch everytime the preferences panel draws down to the file-system
_cached_deployment_version = None


def get_deployment_version():
    global _cached_deployment_version
    if _cached_deployment_version is None:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        deployment_version_filename = os.path.join(script_dir, "deployment-version.txt")
        try:
            with open(deployment_version_filename) as f:
                _cached_deployment_version = f.read()
        except OSError:
            _cached_deployment_version = "Unknown"
    return _cached_deployment_version


def wait_for_debugger_attached():
    """ Waits until a debugger on VSCode's default port is connected and then continues execution """
    import debugpy
    # 5678 is the default attach port in the VS Code debug configurations.
    # Unless a host and port are specified, host defaults to 127.0.0.1
    debugpy.listen(5678)
    print("Waiting for debugger attach")
    debugpy.wait_for_client()
