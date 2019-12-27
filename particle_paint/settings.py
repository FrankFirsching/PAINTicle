from bpy.props import FloatProperty
from bpy.props import PointerProperty
from bpy.types import PropertyGroup
from particle_paint.physics import Physics

class Settings(PropertyGroup):
    """ The settings object for the particle paint tool """
    particle_size: FloatProperty(name="Particle size",
                                 description="The maximum size of an individual particle.",
                                 default=2, min=0.0, soft_min=0.0, soft_max=100,
                                 options=set())
    particle_size_random: FloatProperty(name="Particle size randomization",
                                        description="The possible size variation of the particles.",
                                        default=1, min=0.0, soft_min=0.0, soft_max=100,
                                        options=set())
    max_age: FloatProperty(name="Particle maximum age",
                           description="The maximum age of an individual particle.",
                           default=2, min=0.0, soft_min=0.0, soft_max=100,
                           options=set())
    max_age_random: FloatProperty(name="Particle maximum age randomization",
                                  description="The age variation of an individual particle.",
                                  default=1, min=0.0, soft_min=0.0, soft_max=100,
                                  options=set())
    physics: PointerProperty(type=Physics, name="Physics",
                             description="The physical properties of the simulation",
                             options=set())