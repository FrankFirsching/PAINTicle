# The particle painter, that's using the gpu directly

# <pep8 compliant>

from . import particle_painter
from . import gpu_utils
from . import dependencies
from . import particle
from . import utils

import bpy
import gpu
import mathutils

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
        self.framebuffer = None
        self.last_active_image_slot = None
        self.preview_shader = gpu_utils.load_shader("particle3d", self.glcontext, ["particle"])
        self.paint_shader = gpu_utils.load_shader("particle2d", self.glcontext, ["particle"])
        self.vertex_buffer = self.glcontext.buffer(reserve=1)
        self.paint_vertex_array = self.vao_definition(self.paint_shader)
        # A hack for the update problem
        self.roll_factor = 1
        self.use_preview = False
        if ParticlePainterGPU.draw_handler is None and self.use_preview:
            ParticlePainterGPU.draw_handler = bpy.types.SpaceView3D.draw_handler_add(ParticlePainterGPU._draw_viewport, (self,), "WINDOW", "POST_VIEW")

    def shutdown(self):
        if ParticlePainterGPU.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(ParticlePainterGPU.draw_handler, "WINDOW")
            ParticlePainterGPU.draw_handler = None

    def _draw_viewport(self):
        """ Callback function from blender to draw our particles into the viewport. Don't call by yourself! """
        self.glcontext.point_size = 10
        self.glcontext.depth_func = "<="
        self.glcontext.enable(moderngl.Context.BLEND | moderngl.Context.DEPTH_TEST)
        # We somehow need to recreate the vao every time, since otherwise the vertex buffers are not going to be
        # activated and some other one from blender is the active buffer.
        preview_vertex_array = self.vao_definition(self.preview_shader)
        preview_vertex_array.render(moderngl.vertex_array.POINTS)

    def draw(self, particles):
        num_particles = len(particles)
        self.update_framebuffer()
        self.update_vertex_buffer(particles)
        self.update_uniforms()
        if num_particles == 0:
            return  # Nothing to draw
        if self.use_preview:
            self.update_blender_viewport()
        else:
            scope = self.glcontext.scope(framebuffer=self.framebuffer, enable=moderngl.Context.BLEND)
            with scope:
                self.paint_vertex_array.render(moderngl.vertex_array.POINTS, num_particles)
            self.write_blender_image()

    def update_framebuffer(self):
        image = self.get_active_image()
        image_size = gpu_utils.max_image_size(image)
        if (self.framebuffer is None or
                image_size[0] != self.framebuffer.width or
                image_size[1] != self.framebuffer.height):
            self.framebuffer = gpu_utils.gpu_framebuffer_for_image(image, self.glcontext)
        image_slot = self.get_active_image_slot()
        if image_slot != self.last_active_image_slot:
            # Fill the original image into the framebuffer
            data = array.array("f", image.pixels)
            self.framebuffer.color_attachments[0].write(data)
            self.last_active_image_slot = image_slot

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

    def update_uniforms(self):
        width = self.framebuffer.width
        height = self.framebuffer.height
        brush = self.get_active_brush()
        self.paint_shader["image_size"] = (width, height)
        self.paint_shader["strength"] = brush.strength
        self.paint_shader["particle_size_age_factor"] = self.get_particle_settings().particle_size_age_factor

        model_view_projection = self.context.region_data.perspective_matrix
        self.preview_shader["model_view_projection"] = utils.matrix_to_tuple(model_view_projection)
        self.preview_shader["strength"] = brush.strength

    def write_blender_image_pixels(self, pixels):
        image = self.get_active_image()
        image.pixels.foreach_set(pixels)

    def write_blender_image(self):
        scope = self.glcontext.scope(framebuffer=self.framebuffer, enable=moderngl.Context.BLEND)
        with scope:
            width = self.framebuffer.width
            height = self.framebuffer.height
            pixels = gpu_utils.read_pixel_data_from_framebuffer(width, height, self.framebuffer)
            self.write_blender_image_pixels(pixels)
        self.update_blender_viewport()

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
