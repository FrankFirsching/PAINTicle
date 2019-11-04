# The particle physics settings

import mathutils

class Physics:
    """ The settings for the particle physics """
    def __init__(self):
        self.gravity = mathutils.Vector((0,0,-9.81))
        self.gravityNormalized = self.gravity.normalized()