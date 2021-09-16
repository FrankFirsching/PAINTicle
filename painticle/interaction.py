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


from . import utils

import mathutils
import enum

class Interactions(enum.Flag):
    NONE = 0
    EMIT_PARTICLES = enum.auto()


class Frame:
    def __init__(self, origin: mathutils.Vector, direction: mathutils.Vector):
        self.origin = origin
        self.up, self.right, self.direction = utils.orthogonalize(direction)


class SourceInput:
    """ A class storing the interactive inputs, during painting """
    def __init__(self, origin: mathutils.Vector = mathutils.Vector((0, 0, 0)),
                 direction: mathutils.Vector = mathutils.Vector((0, 0, 1)),
                 size: float = 1, interactions: Interactions = Interactions.NONE,
                 pressure: float = 1):
        self.updateData(origin, direction, size, interactions, pressure)
        self.start_frame = self.frame

    def updateData(self, origin: mathutils.Vector, direction: mathutils.Vector, size: float, interactions: Interactions,
                   pressure: float):
        self.frame = Frame(origin, direction)
        self.size = size
        self.interactions = interactions
        self.pressure = pressure
