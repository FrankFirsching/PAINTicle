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

# A mesh helper class, that allows easy acccess to triangles of polys

import mathutils

import numpy as np

from .utils import Error
from . import bvh


class TriangleMesh:
    """ A class providing additional mesh operations as blende does. It supports e.g. efficient finding of the triangle
        if only a point and polygon id is being given. """

    def __init__(self, context):
        self.object = context.object
        mesh = self.object.data
        if (not mesh.polygons):
            raise Error("ERROR: Mesh doesn't have polygons")
        self.mesh = mesh
        self.mesh.calc_normals_split()
        self.mesh.calc_loop_triangles()
        self.build_bvh(context)


    def build_bvh(self, context):
        points = np.empty((len(self.mesh.vertices), 3), dtype=np.single)
        self.mesh.vertices.foreach_get("co", np.reshape(points, len(self.mesh.vertices)*3))
        triangles = np.empty(len(self.mesh.loop_triangles)*3, dtype=np.uintc)
        self.mesh.loop_triangles.foreach_get("vertices", triangles)
        normals = np.empty(len(self.mesh.loop_triangles)*9, dtype=np.single)
        self.mesh.loop_triangles.foreach_get("split_normals", normals)
        self.bvh = bvh.build_bvh(points, triangles, normals)
