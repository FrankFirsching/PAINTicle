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

from . import particle_painter
from . import gpu_utils
from . import dependencies
from . import particle
from . import utils
from . import preferences
from .utils import Error

import bpy
import gpu
import mathutils
import bgl
import numpy as np

import array
import struct
import typing
import moderngl


class MeshBuffers:
    def __init__(self, glcontext, shader):
        self.glcontext = glcontext
        self.shader = shader
        self.vertices = glcontext.buffer(reserve=1)
        self.uv = glcontext.buffer(reserve=1)
        self.indices = glcontext.buffer(reserve=1)

    def draw(self):
        vao = self.glcontext.vertex_array(self.shader,
                                          [(self.vertices, '3f', 'vertex'),
                                           (self.uv, '2f', 'uv')],
                                          index_buffer=self.indices)
        vao.render(moderngl.vertex_array.TRIANGLES)


class ParticlePainterGPU(particle_painter.ParticlePainter):
    """ This particle painter is using the GPU to draw the particles. """

    draw_handler = None

    def __init__(self, context: bpy.types.Context):
        super().__init__(context)
        # Fetch preferences:
        # We're using the area of the image as preview threshold, preference specifies the edge length
        self.preview_threshold = preferences.get_instance(context).preview_threshold_edge
        self.preview_threshold *= self.preview_threshold
        self.preview_mode = preferences.get_instance(context).preview_mode
        # Setup common GL stuff
        self.glcontext = moderngl.create_context()
        self.paintbuffer = None
        self.paintbuffer_sampler = None
        self.undoimage = None  # Managing own undo, since blender's undo system won't capture image changes correctly
        self.from_new_sim = True  # A flag if we're painting from an empty simulation (used to manage undo image)
        self.last_active_image_slot = None
        preview_shader_name = "particle3d" if self.preview_mode == "particles" else "texture_preview"
        self.preview_shader = gpu_utils.load_shader(preview_shader_name, self.glcontext, ["utils", "particle"])
        self.paint_shader = gpu_utils.load_shader("particle2d", self.glcontext, ["utils", "particle"])
        self.vertex_buffer = self.glcontext.buffer(reserve=1)
        self.paint_vertex_array = self.vao_definition_particles(self.paint_shader)
        self.paintbuffer_changed = False
        # The mesh vbo data, in case preview mode is texture_preview
        self.mesh_buffers = None
        if self.preview_mode == "texture_overlay":
            self.mesh_buffers = MeshBuffers(self.glcontext, self.preview_shader)
        self.build_mesh_vbo(self.get_active_mesh())
        # A hack for the update problem
        self.roll_factor = 1
        self.use_preview = False
        self.update_paintbuffer()

    def shutdown(self):
        self.write_blender_image()
        self.set_use_preview(False)

    def set_use_preview(self, onOff):
        if self.use_preview == onOff:
            return
        if ParticlePainterGPU.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(ParticlePainterGPU.draw_handler, "WINDOW")
            ParticlePainterGPU.draw_handler = None
        self.use_preview = onOff
        if ParticlePainterGPU.draw_handler is None and self.use_preview:
            ParticlePainterGPU.draw_handler = bpy.types.SpaceView3D.draw_handler_add(ParticlePainterGPU._draw_viewport,
                                                                                     (self,), "WINDOW", "POST_VIEW")

    def _draw_viewport(self):
        """ Callback function from blender to draw our particles into the viewport. Don't call by yourself! """
        self.update_preview_uniforms()
        # Need to use bgl here, since blender hangs, if we change state using moderngl
        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glEnable(bgl.GL_BLEND)
        if self.preview_mode == "particles":
            bgl.glDepthMask(False)
            bgl.glEnable(bgl.GL_PROGRAM_POINT_SIZE)
            # We somehow need to recreate the vao every time, since otherwise the vertex buffers are not going to be
            # activated and some other one from blender is the active buffer.
            preview_vertex_array = self.vao_definition_particles(self.preview_shader)
            preview_vertex_array.render(moderngl.vertex_array.POINTS)
        elif self.preview_mode == "texture_overlay":
            self.paintbuffer_sampler.use()
            self.mesh_buffers.draw()
        else:
            raise Error("Unknown preview_mode!")

    def draw(self, particles, time_step):
        """ Draw the given particles into the paint buffer and sync to blender's image in case we're not in
            preview mode. In preview mode sync to blender's image only if we reached 0 particles again after
            simulation is 'done'. """

        num_particles = len(particles)
        self.update_paintbuffer()
        self.update_vertex_buffer(particles)
        self.update_uniforms(time_step)
        if num_particles == 0:
            if self.paintbuffer_changed:
                self.write_blender_image()
            self.from_new_sim = True  # Next paint call will be from an new simulation
            return  # Nothing to draw

        if self.from_new_sim:
            # Before drawing the first set of particles capture the internal undo image
            self.undoimage = self.capture_active_image()

        # We're either inside a current particle sim or just started a new one, so it's not from new anymore
        self.from_new_sim = False

        # Draw into the texture paint framebuffer
        scope = self.glcontext.scope(framebuffer=self.paintbuffer, enable=moderngl.Context.BLEND)
        with scope:
            self.paintbuffer_changed = True
            self.paint_vertex_array.render(moderngl.vertex_array.POINTS, num_particles)

        if self.use_preview:
            self.context.area.tag_redraw()
        else:
            self.write_blender_image()

    def capture_active_image(self):
        result = None
        source_image = self.get_active_image()
        if source_image is not None:
            result = np.empty(source_image.size[0]*source_image.size[1]*4, dtype=np.float32)
            source_image.pixels.foreach_get(result)
        return result

    def update_paintbuffer(self):
        image = self.get_active_image()
        image_size = gpu_utils.max_image_size(image)
        if (self.paintbuffer is None or
                image_size[0] != self.paintbuffer.width or
                image_size[1] != self.paintbuffer.height):
            if image_size[0] > 0 and image_size[1] > 0:
                self.paintbuffer = gpu_utils.gpu_framebuffer_for_image(image, self.glcontext)
                self.paintbuffer_sampler = self.glcontext.sampler(texture=self.paintbuffer.color_attachments[0])
            else:
                self.paintbuffer = None
                self.paintbuffer_sampler = None
        image_slot = self.get_active_image_slot()
        if image_slot != self.last_active_image_slot and self.paintbuffer is not None:
            # Fill the original image into the paintbuffer
            self.context.window.cursor_modal_set("WAIT")
            data = self.capture_active_image()
            self.paintbuffer.color_attachments[0].write(data)
            self.paintbuffer_changed = False
            self.last_active_image_slot = image_slot
            preview_activated = self.paintbuffer.width*self.paintbuffer.height > self.preview_threshold
            self.set_use_preview(preview_activated)
            self.undoimage = None
            self.context.window.cursor_modal_restore()

    def update_vertex_buffer(self, particles: typing.Iterable[particle.Particle]):
        coords = array.array("f")
        for p in particles:
            self.append_visual_properties(coords, p)
        # We can't resize down to 0, so we use 1 byte length as indication of zero particles
        self.update_vbo(self.vertex_buffer, coords)

    def append_visual_properties(self, vbo_data: array.array, p):
        """ Append the particle's visual properties to the vbo data array. """
        # Also see vao_definition_particles, that provides the glsl schema for the data
        vbo_data.extend(p.location)
        vbo_data.extend(p.uv)
        vbo_data.append(p.particle_size)
        vbo_data.append(p.age)
        vbo_data.append(p.max_age)
        vbo_data.extend(p.color)

    def vao_definition_particles(self, shader):
        """ Generate a vao definition for the given shader """
        # This list needs to conform to the list of attribute written in append_visual_properties
        # The shader library particle_def.glsl also defines these properties.
        attribs = [("location", 3),
                   ("uv", 2),
                   ("size", 1),
                   ("age", 1),
                   ("max_age", 1),
                   ("color", 3)]
        sizes = []
        names = []
        for attrib in attribs:
            if attrib[0] in shader:
                x = "{}f".format(attrib[1])
                names.append(attrib[0])
            else:
                x = "{}x".format(attrib[1]*4)  # We use floats, so padding is 4 bytes per float
            sizes.append((x))
        return self.glcontext.vertex_array(shader, [(self.vertex_buffer, " ".join(sizes), *names)])

    def update_uniforms(self, time_step):
        width = self.paintbuffer.width
        height = self.paintbuffer.height
        brush = self.get_active_brush()
        self.paint_shader["image_size"] = (width, height)
        self.paint_shader["strength"] = brush.strength
        self.paint_shader['time_step'] = time_step
        self.paint_shader["particle_size_age_factor"] = self.get_particle_settings().particle_size_age_factor

    def update_preview_uniforms(self):
        model_view_projection = self.context.region_data.perspective_matrix
        self.preview_shader["model_view_projection"] = utils.matrix_to_tuple(model_view_projection)
        if self.preview_mode == "particles":
            self.preview_shader["particle_size_age_factor"] = self.get_particle_settings().particle_size_age_factor
        elif self.preview_mode == "texture_overlay":
            pass
        else:
            raise Error("Unknown preview_mode!")

    def write_blender_image_pixels(self, pixels):
        image = self.get_active_image()
        image.pixels.foreach_set(pixels)

    def write_blender_image(self):
        scope = self.glcontext.scope(framebuffer=self.paintbuffer, enable=moderngl.Context.BLEND)
        with scope:
            width = self.paintbuffer.width
            height = self.paintbuffer.height
            pixels = gpu_utils.read_pixel_data_from_framebuffer(width, height, self.paintbuffer)
            self.write_blender_image_pixels(pixels)
        self.paintbuffer_changed = False
        self.update_blender_viewport()

    def undo_last_paint(self):
        if self.undoimage is not None:
            self.paintbuffer.color_attachments[0].write(self.undoimage)
            self.paintbuffer_changed = True
            self.write_blender_image()

    def update_blender_viewport(self):
        # BIG HACK: None of the update, gl_touch methods of the image
        # and neither tag_redraw of the view_3d functions work to trigger
        # rerendering the view. So we wiggle the view a very small amount around
        # the view axis. To not accumulate the small amounts and get a drift, we
        # introduced the roll_factor member variable. As soon as this hack is gone,
        # we can also remove that variable.

        # not working: self.context.area.tag_redraw()
        self.roll_factor = -1 if self.roll_factor > 0 else 1
        bpy.ops.view3d.view_roll(angle=0.000005*self.roll_factor)

    def build_mesh_vbo(self, mesh: bpy.types.Mesh):
        if self.mesh_buffers is None:
            return  # Nothing to do, since we're not painting the mesh

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

        self.update_vbo(self.mesh_buffers.vertices, vertices)
        self.update_vbo(self.mesh_buffers.uv, uv)
        self.update_vbo(self.mesh_buffers.indices, indices)

    def update_vbo(self, buffer, data):
        """ A utility function to update a vertex buffer """
        vbo_data = data.tobytes()
        new_size = max(1, len(vbo_data))
        buffer.orphan(new_size)
        buffer.write(vbo_data)
