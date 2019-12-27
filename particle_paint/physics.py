from bpy.props import FloatVectorProperty
from bpy.types import PropertyGroup

import mathutils

def onUpdatePhysicsGravity(self, context):
    self.gravityNormalized = mathutils.Vector(self.gravity).normalized()

class Physics(PropertyGroup):
    """ The settings for the particle physics """

    gravity: FloatVectorProperty(name="Gravity",
                                 description="The gravitational force applied to the particles.",
                                 default=(0,0,-9.81), options=set(),
                                 subtype="ACCELERATION", unit="ACCELERATION",
                                 update=onUpdatePhysicsGravity)

    gravityNormalized: FloatVectorProperty(name="Gravity (normalized)",
                                 description="The normalized gravitational force applied to the particles.",
                                 default=(0,0,-1), options=set(['HIDDEN']),
                                 subtype="ACCELERATION", unit="ACCELERATION")
