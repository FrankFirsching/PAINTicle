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

from . import meshbuffer
from . import gpu_utils

import moderngl


class Overbaker:
    """ This class provides support for overbaking the painted results. """

    def __init__(self, meshbuffer: meshbuffer.MeshBuffer, glcontext: moderngl.Context):
        self.meshbuffer = meshbuffer
        self.glcontext = glcontext
        self.shader = gpu_utils.load_compute_shader("overbaker", self.glcontext, ["utils"])
        self.mask_texture = None

    def overbake(self, texture: moderngl.Texture, steps: int):
        #self.printTexture("INPUT_TEXTURE", texture)
        self._init_overbake(texture)
        for i in range(steps):
            self._overbake_once(texture, i)
        #self.printTexture("END_MASK", self.mask_texture)
        self._shutdown_overbake(texture)
        #self.printTexture("OUTPUT_TEXTURE", texture)

    def _init_overbake(self, texture: moderngl.Texture):
        # Initialize mask
        self.mask_texture = self.glcontext.texture(texture.size, 1, dtype='u1')
        framebuffer = self.glcontext.framebuffer(color_attachments=[self.mask_texture])
        init_shader = gpu_utils.load_shader("initoverbaker", self.glcontext)
        scope = self.glcontext.scope(framebuffer=framebuffer)
        with scope:
            self.meshbuffer.draw(init_shader)
        #self.printTexture("MASK:", self.mask_texture)

    def printTexture(self, note, texture: moderngl.Texture):
        import numpy as np
        data = np.frombuffer(texture.read(), dtype=texture.dtype)
        data = data.reshape((texture.size[0], texture.size[1], texture.components))
        print(note, "size=", texture.size, "components=", texture.components, "dtype=", texture.dtype)
        for i in range(texture.components):
            print("Component", i)
            print(data[:, :, i])

    def _overbake_once(self, texture: moderngl.Texture, step: int):
        texture.bind_to_image(0, read=True, write=True)
        self.mask_texture.bind_to_image(1, read=True, write=True)
        w, h = texture.size
        nx, ny = int(w/16), int(h/16)
        # We need to add 2, since 0 is reserved for empty pixels and we initialized our inner mask with 1
        self.shader['step'] = step+2
        self.shader.run(nx, ny, 1)
        # moderngl doesn't expose glMemoryBarrier, so we need to use the less efficient glFinish to synchronize :-(
        self.glcontext.finish()

    def _shutdown_overbake(self, texture: moderngl.Texture):
        self.mask_texture = None
