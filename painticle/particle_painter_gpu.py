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

from . import numpyutils
from . import particle_painter
from . import gpu_utils
from . import dependencies
from . import accel
from . import utils
from . import meshbuffer
from . import overbaker
from .settings import preferences
from .sim import particle_simulator
from .utils import Error

import bpy
import bgl
import numpy as np
import struct

import moderngl


class ParticlePainterGPU(particle_painter.ParticlePainter):
    """ This particle painter is using the GPU to draw the particles. """

    draw_handler = None
    draw_handler_text = None

    def __init__(self, context: bpy.types.Context, simulator: particle_simulator.ParticleSimulator):
        super().__init__(context, simulator)
        # Fetch preferences:
        # We're using the area of the image as preview threshold, preference specifies the edge length
        self.preview_threshold = preferences.get_instance(context).preview_threshold_edge
        self.preview_threshold *= self.preview_threshold
        self.preview_mode = preferences.get_instance(context).preview_mode
        self.overlay_preview_opacity = preferences.get_instance(context).overlay_preview_opacity
        # Setup common GL stuff
        self.glcontext = moderngl.create_context()
        self.paintbuffer = None
        self.paintbuffer_sampler = None
        self.undoimage = None  # Managing own undo, since blender's undo system won't capture image changes correctly
        self.from_new_sim = True  # A flag if we're painting from an empty simulation (used to manage undo image)
        self.last_active_image_slot = None
        preview_shader_name = "particle3d" if self.preview_mode == "particles" else "texture_preview"
        self.preview_shader = gpu_utils.load_shader(preview_shader_name, self.glcontext, ["utils", "particle"])
        self.paint_shader = gpu_utils.load_shader("particle2d", self.glcontext, ["utils", "particle", "gridhash"])
        self.particles_buffer = self.glcontext.buffer(reserve=1)
        self.paintbuffer_changed = False
        self.mesh_buffer = meshbuffer.MeshBuffer(self.glcontext, self.paint_shader)
        self.mesh_buffer.build_mesh_vbo(self.get_active_mesh())
        # Setup hashed grid and the GPU buffers for it
        self.hashed_grid_buffer = self.glcontext.buffer(reserve=1)
        # A hack for the update problem
        self.roll_factor = 1
        self.use_preview = False
        if ParticlePainterGPU.draw_handler_text is None:
            self.context.area.tag_redraw()
            ParticlePainterGPU.draw_handler_text = \
                bpy.types.SpaceView3D.draw_handler_add(ParticlePainterGPU._draw_viewport_text,
                                                       (self,), "WINDOW", "POST_PIXEL")
        self.update_paintbuffer()

    def shutdown(self):
        # self.write_blender_image()
        self.set_use_preview(False)
        if ParticlePainterGPU.draw_handler_text is not None:
            bpy.types.SpaceView3D.draw_handler_remove(ParticlePainterGPU.draw_handler_text, "WINDOW")
            ParticlePainterGPU.draw_handler_text = None

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
        if not self.is_sim_active():
            return
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
            self.mesh_buffer.draw(self.preview_shader)
        else:
            raise Error("Unknown preview_mode!")

    def _draw_viewport_text(self):
        """ Callback function from blender to draw UI elements """
        if self.is_sim_active():
            gpu_utils.draw_text(self.context, 10, 10, 24, "Simulating...", (1, 0.5, 0.5, 0.5))
        else:
            gpu_utils.draw_text(self.context, 10, 10, 24, "PAINTicle active", (0, 0, 0, 0.5))

    def is_sim_active(self):
        """ A simulation is active, if the next draw call is not starting a new sim """
        return not self.from_new_sim

    def draw(self, particles, time_step):
        """ Draw the given particles into the paint buffer and sync to blender's image in case we're not in
            preview mode. In preview mode sync to blender's image only if we reached 0 particles again after
            simulation is 'done'. """

        num_particles = particles.num_particles
        self.update_paintbuffer()
        self.update_particles_buffer(particles)
        self.update_paint_shader_uniforms(time_step)
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
            # We already premultiply in shader blending
            self.glcontext.blend_func = (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA,
                                         moderngl.ONE, moderngl.ONE)
            self.paintbuffer_changed = True
            self.mesh_buffer.draw()

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

    def update_particles_buffer(self, particles):
        # This list needs to conform to the list of attribute written in vao_definition_particles
        # The shader library particle_def.glsl also defines these properties.
        padding = np.empty(particles.age.size, dtype=numpyutils.float32_dtype)
        coords = np.column_stack((numpyutils.unstructured(particles.location),
                                  numpyutils.unstructured(particles.size),
                                  numpyutils.unstructured(particles.uv),
                                  numpyutils.unstructured(particles.age),
                                  numpyutils.unstructured(particles.max_age),
                                  numpyutils.unstructured(particles.color),
                                  numpyutils.unstructured(padding)))
        gpu_utils.update_vbo(self.particles_buffer, coords)

    def vao_definition_particles(self, shader):
        """ Generate a vao definition for the given shader """
        # This list needs to conform to the list of attribute written in update_vertex_buffer
        # The shader library particle_def.glsl also defines these properties.
        attribs = [("location", 3),
                   ("size", 1),
                   ("uv", 2),
                   ("age", 1),
                   ("max_age", 1),
                   ("color", 3),
                   ("padding", 1)]
        sizes = []
        names = []
        for attrib in attribs:
            if attrib[0] in shader:
                x = "{}f".format(attrib[1])
                names.append(attrib[0])
            else:
                x = "{}x".format(attrib[1]*4)  # We use floats, so padding is 4 bytes per float
            sizes.append((x))
        return self.glcontext.vertex_array(shader, [(self.particles_buffer, " ".join(sizes), *names)])

    def update_paint_shader_uniforms(self, time_step):
        self.update_hashed_grid_buffer()
        self.particles_buffer.bind_to_storage_buffer(1)
        brush = self.get_active_brush()
        self.paint_shader["strength"] = brush.strength
        self.paint_shader['time_step'] = time_step
        self.paint_shader["particle_size_age_factor"] = self.get_particle_size_age_factor()

    def update_hashed_grid_buffer(self):
        hashed_grid = self.simulator.hashed_grid
        fixed_struct = struct.pack("fI", hashed_grid.voxel_size, hashed_grid.num_particles)
        fixed_struct_size = len(fixed_struct)
        cell_offsets = hashed_grid.cell_offsets
        cell_offsets_size = len(cell_offsets)*4  # floats have 4 bytes
        sorted_particle_ids = hashed_grid.sorted_particle_ids
        sorted_particle_ids_size = len(sorted_particle_ids)*2*4  # 2 unsigned int with each 4 bytes
        self.hashed_grid_buffer.orphan(fixed_struct_size+cell_offsets_size+sorted_particle_ids_size)
        self.hashed_grid_buffer.write(fixed_struct, offset=0)
        self.hashed_grid_buffer.write(cell_offsets, offset=fixed_struct_size)
        self.hashed_grid_buffer.write(sorted_particle_ids, offset=fixed_struct_size+cell_offsets_size)
        self.hashed_grid_buffer.bind_to_storage_buffer(0)

    def update_preview_uniforms(self):
        model_view_projection = self.context.region_data.perspective_matrix @ self.get_active_object().matrix_world
        self.preview_shader["model_view_projection"] = utils.matrix_to_tuple(model_view_projection)
        if self.preview_mode == "particles":
            height = self.paintbuffer.height
            self.preview_shader["image_height"] = height
            self.preview_shader["projection"] = utils.matrix_to_tuple(self.context.region_data.window_matrix)
            self.preview_shader["particle_size_age_factor"] = self.get_particle_size_age_factor()
        elif self.preview_mode == "texture_overlay":
            self.preview_shader["opacity"] = self.overlay_preview_opacity
        else:
            raise Error("Unknown preview_mode!")

    def write_blender_image_pixels(self, pixels):
        image = self.get_active_image()
        image.pixels.foreach_set(pixels)

    def write_blender_image(self):
        baker = overbaker.Overbaker(self.mesh_buffer, self.glcontext)
        baker.overbake(self.paintbuffer.color_attachments[0], 4)
        pixels = gpu_utils.read_pixel_data_from_framebuffer(self.paintbuffer, self.glcontext)
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
        override = {
            'area': self.context.area,
            'region': self.context.region,
        }
        bpy.ops.view3d.view_roll(override, angle=0.000005*self.roll_factor)
