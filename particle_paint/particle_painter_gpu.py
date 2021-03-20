# The particle painter, that's using the gpu directly

# <pep8 compliant>

from . import particle_painter
from . import gpu_utils
from . import dependencies
from . import particle

import bpy

import array
import struct
import typing
import moderngl


class ParticlePainterGPU(particle_painter.ParticlePainter):
    """ This particle painter is using the GPU to draw the particles. """

    def __init__(self, context: bpy.types.Context):
        super().__init__(context)
        self.glcontext = moderngl.create_context()
        self.framebuffer = None
        self.last_active_image_slot = None
        self.shader = gpu_utils.load_shader("particle", self.glcontext)
        self.vertex_buffer = self.glcontext.buffer(reserve=1)
        self.vertex_array = self.glcontext.vertex_array(self.shader, self.vertex_buffer, "p.uv", "p.size", "p.age", "p.max_age", "p.color")
        self.counter = 0
        # A hack for the update problem
        self.roll_factor = 1

    def draw(self, particles):
        num_particles = len(particles)
        self.update_framebuffer()
        self.update_vertex_buffer(particles)
        if self.vertex_buffer is None:
            return  # Nothing to draw
        self.update_uniforms()
        # brush = self.get_active_brush()
        # strength = brush.strength
        # brushColor = brush.color
        scope = self.glcontext.scope(framebuffer=self.framebuffer, enable=moderngl.Context.BLEND)
        with scope:
            # self.glcontext.clear()
            self.vertex_array.render(moderngl.vertex_array.POINTS, num_particles*2)

            width = self.framebuffer.width
            height = self.framebuffer.height
            # Only save every 25th image for debuggin purposes
            pixels = gpu_utils.read_pixel_data_from_framebuffer(width, height, self.framebuffer)
            self.update_image_from_pixels(pixels)

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
            p.append_visual_properties(coords)
        vbo_data = coords.tobytes()
        self.vertex_buffer.orphan(len(vbo_data))
        self.vertex_buffer.write(vbo_data)

    def update_uniforms(self):
        width = self.framebuffer.width
        height = self.framebuffer.height
        brush = self.get_active_brush()
        self.shader["image_size"] = (width, height)

    def update_image_from_pixels(self, pixels):
        image = self.get_active_image()
        image.pixels.foreach_set(pixels)

        # BIG HACK: None of the update, gl_touch methods of the image 
        # and neither tag_redraw of the view_3d functions work to trigger
        # rerendering the view. So we wiggle the view a very small amount around
        # the view axis. To not accumulate the small amounts and get a drift, we
        # introduced the roll_factor member variable. As soon as this hack is gone,
        # we can also remove that variable.

        # not working: self.context.area.tag_redraw()
        self.roll_factor = -1 if self.roll_factor > 0 else 1
        bpy.ops.view3d.view_roll(angle=0.000005*self.roll_factor)

