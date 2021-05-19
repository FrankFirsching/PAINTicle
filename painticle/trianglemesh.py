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

import bpy
import mathutils
import sys

from painticle.utils import Error


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
        self.build_poly_maps()
        depsgraph = context.evaluated_depsgraph_get()
        self.bvh = mathutils.bvhtree.BVHTree.FromObject(self.object, depsgraph)

    def triangle_for_point_on_poly(self, p, face_index):
        eps = 0.0
        tessellated = self.poly_to_tri[face_index]
        for passes in range(2):
            for tri_index in tessellated:
                bary = self.barycentrics(p, tri_index)
                if bary[0] >= eps and bary[1] >= eps and bary[2] >= eps:
                    return tri_index
            # Sometimes, we get a point slightly outside of a polygon, let's
            # treat it as good as possible.
            eps = -0.0001
        print("WARNING: Couldn't find triangle for", p, "on", face_index)
        return None

    def barycentrics(self, p, tri_index,
                     b0=mathutils.Vector((1, 0, 0)),
                     b1=mathutils.Vector((0, 1, 0)),
                     b2=mathutils.Vector((0, 0, 1))):
        tri = self.mesh.loop_triangles[tri_index].vertices
        verts = self.mesh.vertices
        return mathutils.geometry.barycentric_transform(p, verts[tri[0]].co, verts[tri[1]].co, verts[tri[2]].co,
                                                        b0, b1, b2)

    def build_poly_maps(self):
        """ Builds 2 maps, that allow mapping from triangles to polygons and
            vice versa. """
        self.poly_to_tri = [None]*len(self.mesh.polygons)
        self.tri_to_poly = [None]*len(self.mesh.loop_triangles)
        for tri in self.mesh.loop_triangles:
            self.tri_to_poly[tri.index] = tri.polygon_index
            if self.poly_to_tri[tri.polygon_index] is not None:
                self.poly_to_tri[tri.polygon_index].append(tri.index)
            else:
                self.poly_to_tri[tri.polygon_index] = [tri.index]

    def edgeStart(self, edgeId):
        return self.mesh.loop_triangles[edgeId//3].vertices[edgeId % 3]

    def edgeEnd(self, edgeId):
        return self.mesh.loop_triangles[edgeId//3].vertices[(edgeId+1) % 3]
