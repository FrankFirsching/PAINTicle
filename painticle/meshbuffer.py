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

# The particle painter, that's using the gpu directly

# <pep8 compliant>



from . import gpu_utils
from .utils import Error

import bpy
import numpy as np

import moderngl


class MeshBuffer:
    def __init__(self, glcontext, shader):
        self.glcontext = glcontext
        self.shader = shader
        self.vertices = glcontext.buffer(reserve=1)
        self.uv = glcontext.buffer(reserve=1)
        self.indices = glcontext.buffer(reserve=1)

    def draw(self, shader=None):
        shader = shader if shader is not None else self.shader
        buffers = []
        if "vertex" in shader:
            buffers.append((self.vertices, '3f', 'vertex'))
        if "uv" in shader:
            buffers.append((self.uv, '2f', 'uv'))
        vao = self.glcontext.vertex_array(shader, buffers, index_buffer=self.indices)
        vao.render(moderngl.vertex_array.TRIANGLES)

    def build_mesh_vbo(self, mesh: bpy.types.Mesh):
        if mesh is None:
            return  # Nothing to do, if we didn't get an active mesh

        if (not mesh.polygons):
            raise Error("ERROR: Mesh doesn't have polygons")

        v = np.empty((len(mesh.vertices), 3), 'f')
        mesh.vertices.foreach_get("co", np.reshape(v, len(mesh.vertices)*3))

        uvMap = mesh.uv_layers.active.data
        uv = np.empty((len(uvMap), 2), 'f')
        uvMap.foreach_get("uv", np.reshape(uv, len(uvMap)*2))

        vindices = np.empty(len(mesh.loop_triangles)*3, 'i')
        mesh.loop_triangles.foreach_get("vertices", vindices)
        indices = np.empty(len(mesh.loop_triangles)*3, 'i')
        mesh.loop_triangles.foreach_get("loops", indices)

        # We need to shuffle the vertices into the loop indices
        vert_ind = np.empty(indices.max()+1, 'i')
        np.put(vert_ind, indices, vindices)
        vertices = np.take(v, vert_ind, 0)

        gpu_utils.update_vbo(self.vertices, vertices)
        gpu_utils.update_vbo(self.uv, uv)
        gpu_utils.update_vbo(self.indices, indices)
