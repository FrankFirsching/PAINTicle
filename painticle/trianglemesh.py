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

# A mesh helper class, that allows easy acccess to triangles of polys and to
# neighbors of a triangle

import bpy
import mathutils
import sys

from painticle.utils import Error

class TriangleMesh:
    def __init__(self, object):
        self.object = object
        mesh = object.data
        if (not mesh.polygons):
            raise Error("ERROR: Mesh doesn't have polygons")
        self.mesh = mesh
        self.mesh.calc_normals_split()
        self.mesh.calc_loop_triangles()
        self.build_poly_maps()
        self.build_back_refs()
        self.build_neighbor_infos()

    def triangle_for_point_on_poly(self, p, face_index):
        eps = 0.0
        tessellated = self.poly_to_tri[face_index]
        for passes in range(2):
            for tri_index in tessellated:
                bary = self.barycentrics(p, tri_index)
                if bary[0]>=eps and bary[1]>=eps and bary[2]>=eps:
                    return tri_index
            # Sometimes, we get a point slightly outside of a polygon, let's
            # treat it as good as possible.
            eps = -0.0001
        print("WARNING: Couldn't find triangle for",p,"on",face_index)
        return None

    def barycentrics(self, p, tri_index,
                     b0=mathutils.Vector((1, 0, 0)),
                     b1=mathutils.Vector((0, 1, 0)),
                     b2=mathutils.Vector((0, 0, 1))):
        tri = self.mesh.loop_triangles[tri_index]
        tri_p = [self.mesh.vertices[i].co for i in tri.vertices]
        return mathutils.geometry.barycentric_transform(p, tri_p[0], tri_p[1], tri_p[2], b0, b1, b2)

    def project_point_to_triangle(self, p, tri_index):
        tri = self.mesh.loop_triangles[tri_index]
        tri_p = [self.mesh.vertices[i].co for i in tri.vertices]
        n = tri.normal
        v = tri_p[0]-p
        offset = v.project(n)
        p_new = p+offset
        return p_new

    def move_over_triangle_boundaries(self, old_p, p, tri_index):
        # we should wrap the distance old_p -> p onto the mesh and not just
        # project p onto the next triangle
        baries = self.barycentrics(p, tri_index)
        visited_triangles = set()
        while not all(bary > 0 for bary in baries) and \
              not tri_index in visited_triangles:
            visited_triangles.add(tri_index)
            neighbors = self.neighbors[tri_index]
            if baries[0] < 0:
                if neighbors[1] is not None:
                    tri_index = neighbors[1]//3
                else:
                    return p, tri_index, False
            elif baries[1] < 0:
                if neighbors[2] is not None:
                    tri_index = neighbors[2]//3
                else:
                    return p, tri_index, False
            elif baries[2] < 0:                
                if neighbors[0] is not None:
                    tri_index = neighbors[0]//3
                else:
                    return p, tri_index, False
            else:
                raise Error("ERROR: Barycentrics invalid.")
            p = self.project_point_to_triangle(p, tri_index)
            baries = self.barycentrics(p, tri_index)
        return p, tri_index, True

    def build_poly_maps(self):
        """ Builds 2 maps, that allow mapping from triangles to polygons and
            vice versa. """
        self.poly_to_tri = [None]*len(self.mesh.polygons)
        self.tri_to_poly = [None]*len(self.mesh.loop_triangles)
        for tri in self.mesh.loop_triangles:
            self.tri_to_poly[tri.index] = tri.polygon_index
            if self.poly_to_tri[tri.polygon_index]!=None:
                self.poly_to_tri[tri.polygon_index].append(tri.index)
            else:
                self.poly_to_tri[tri.polygon_index] = [tri.index]

    def build_back_refs(self):
        """ Builds map, that allows to query all outgoing edges of a vertex """
        self.back_refs = [None]*len(self.mesh.vertices)
        for tri in self.mesh.loop_triangles:
            for i in range(3):
                v = tri.vertices[i]
                if self.back_refs[v] is not None:
                    self.back_refs[v].append(tri.index*3+i)
                else:
                    self.back_refs[v] = [tri.index*3+i]

    def build_neighbor_infos(self):
        """ Builds map, that specifies the neighbor edges of a triangle edge """
        self.neighbors = [None]*len(self.mesh.loop_triangles)
        for tri in self.mesh.loop_triangles:
            neighbors = [None]*3
            for i in range(3):
                v = tri.vertices[i]
                vNext = tri.vertices[(i+1) % 3]
                possibleNeighbors = self.back_refs[vNext]
                neighboringEdge = None
                for e in possibleNeighbors:
                    if self.edgeEnd(e) == v:
                        neighboringEdge = e
                        break
                neighbors[i] = neighboringEdge
            self.neighbors[tri.index] = neighbors

    def edgeStart(self, edgeId):
        return self.mesh.loop_triangles[edgeId//3].vertices[edgeId % 3]

    def edgeEnd(self, edgeId):
        return self.mesh.loop_triangles[edgeId//3].vertices[(edgeId+1) % 3]