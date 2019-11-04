# A mesh helper class, that allows easy acccess to triangles of polys and to
# neighbors of a triangle

import bpy

class TriangleMesh:
    def __init__(self, object):
        self.object = object
        mesh = object.data
        if (not mesh.polygons):
            raise Error("ERROR: Mesh doesn't have polygons")
        self.mesh = mesh
        self.mesh.calc_loop_triangles()
        self.poly_to_tri = {}
        for tri in self.mesh.loop_triangles:
            if tri.polygon_index in self.poly_to_tri:
                self.poly_to_tri[tri.polygon_index].append(tri.index)
            else:
                self.poly_to_tri[tri.polygon_index] = [tri.index]
        
