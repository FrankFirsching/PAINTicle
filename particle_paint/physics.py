from bpy.props import FloatProperty
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

    friction_coefficient: FloatProperty(name="Friction",
                                        description="The friction coefficient (how sticky is the surface).",
                                        min=0.0, soft_max=0.1, default=0.01, options=set())

    initial_speed: FloatProperty(name="Initial Speed",
                                 description="The initial speed of the particles, when they are born.",
                                 min=0.0, soft_max=1, default=0.0, options=set())

    initial_speed_random: FloatProperty(name="Initial Speed randomness",
                                 description="The random factor of the initial speed.",
                                 min=0.0, max=1, default=0.0, options=set())

    max_time_step: FloatProperty(name="Max. Timestep",
                                 description="The maximum time step used for the simulation.",
                                 default=0.04, options=set())

    gravityNormalized: FloatVectorProperty(name="Gravity (normalized)",
                                 description="The normalized gravitational force applied to the particles.",
                                 default=(0,0,-1), options=set(['HIDDEN']),
                                 subtype="ACCELERATION", unit="ACCELERATION")
