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

import bpy
import gpu
import mathutils
import bgl
import numpy as np

import array
import struct
import typing
import moderngl


class ParticlePainterGPU(particle_painter.ParticlePainter):
    """ This particle painter is using the GPU to draw the particles. """

    draw_handler = None

    def __init__(self, context: bpy.types.Context):
        super().__init__(context)
        self.glcontext = moderngl.create_context()
        self.paintbuffer = None
        self.undoimage = None  # Managing own undo, since blender's undo system won't capture image changes correctly
        self.from_new_sim = True  # A flag if we're painting from an empty simulation (used to manage undo image)
        self.last_active_image_slot = None
        self.preview_shader = gpu_utils.load_shader("particle3d", self.glcontext, ["particle"])
        self.paint_shader = gpu_utils.load_shader("particle2d", self.glcontext, ["particle"])
        self.vertex_buffer = self.glcontext.buffer(reserve=1)
        self.paint_vertex_array = self.vao_definition(self.paint_shader)
        self.paintbuffer_changed = False
        # We're using the area of the image as preview threshold, preference specifies the edge length
        self.preview_threshold = preferences.get_instance(context).preview_threshold_edge
        self.preview_threshold *= self.preview_threshold
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
        # Need to use bgl here, since moderngl doesn't allow modifying the depth mask
        bgl.glDepthMask(False)
        # Need to use bgl here, since blender hangs, if we change state using moderngl
        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glEnable(bgl.GL_DEPTH_TEST)
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glEnable(bgl.GL_PROGRAM_POINT_SIZE)
        # We somehow need to recreate the vao every time, since otherwise the vertex buffers are not going to be
        # activated and some other one from blender is the active buffer.
        preview_vertex_array = self.vao_definition(self.preview_shader)
        preview_vertex_array.render(moderngl.vertex_array.POINTS)

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
            else:
                self.paintbuffer = None
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
        vbo_data = coords.tobytes()
        # We can't resize down to 0, so we use 1 byte length as indication of zero particles
        new_size = max(1, len(vbo_data))
        self.vertex_buffer.orphan(new_size)
        self.vertex_buffer.write(vbo_data)

    def append_visual_properties(self, vbo_data: array.array, p):
        """ Append the particle's visual properties to the vbo data array. """
        # Also see vao_definition, that provides the glsl schema for the data
        vbo_data.extend(p.location)
        vbo_data.extend(p.uv)
        vbo_data.append(p.particle_size)
        vbo_data.append(p.age)
        vbo_data.append(p.max_age)
        vbo_data.extend(p.color)

    def vao_definition(self, shader):
        """ Generate a vao definition for the given shader """
        # This list needs to conform to the list of attribute written in append_visual_properties
        # The shader library particle_def.glsl also defines these properties.
        attribs = [("p.location", 3),
                   ("p.uv", 2),
                   ("p.size", 1),
                   ("p.age", 1),
                   ("p.max_age", 1),
                   ("p.color", 3)]
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

        model_view_projection = self.context.region_data.perspective_matrix
        self.preview_shader["model_view_projection"] = utils.matrix_to_tuple(model_view_projection)
        self.preview_shader["particle_size_age_factor"] = self.get_particle_settings().particle_size_age_factor

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
