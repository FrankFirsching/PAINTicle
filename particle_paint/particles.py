# A particles shooter class

from bpy_extras import view3d_utils
import bpy
import mathutils

import array
import math
import random

from . import physics
from . import trianglemesh
from .utils import Error
from . import particle_painter_gpu

from . import particle


class Particles:
    """ A class managing the particle system for the paint operator """
    def __init__(self, context: bpy.types.Context):
        self.rnd = random.Random()
        self.paint_mesh = trianglemesh.TriangleMesh(context.active_object)
        self.matrix = self.paint_mesh.object.matrix_world.copy()
        self.particles = []
        self.painter = particle_painter_gpu.ParticlePainterGPU(context)

    def numParticles(self):
        """ Return the number of simulated particles """
        return len(self.particles)
    
    def shoot(self, context: bpy.types.Context, event, particle_settings):
        """ Shoot particles and paint them """
        paint_size = self.get_brush_size(context)
        angle = 2*math.pi*self.rnd.random()
        distance = paint_size*self.rnd.random()
        offset_x = math.cos(angle)*distance
        offset_y = math.sin(angle)*distance
        ray_origin, ray_direction = self.get_ray(context,
                                                 event.mouse_x+offset_x,
                                                 event.mouse_y+offset_y)
        
        location, normal, face_index = self.ray_cast_on_object(ray_origin,
                                                               ray_direction)
        if location != None:
            tri_index = self.paint_mesh.triangle_for_point_on_poly(location, face_index)
            p = particle.Particle(location, tri_index, self.get_brush_color(context), self.paint_mesh, particle_settings)
            self.add_particle(p)
    
    def move_particles(self, physics, deltaT):
        """ Simulate gravity """
        for i in range(len(self.particles) - 1, -1, -1):
            p = self.particles[i]
            p.move(physics, self.paint_mesh, deltaT)
            if p.age > p.max_age:
                del self.particles[i]

    def paint_particles(self, context: bpy.types.Context):
        """ Paint all particles into the texture """
        self.painter.draw(self.particles)

    def clear_particles(self):
        """ Start with an empty set of particles """
        self.particles = []

    def add_particle(self, particle):
        """ Add a single particle """
        #if len(self.particles)>0:
        #    return
        self.particles.append(particle)

    def get_active_image(self, context: bpy.types.Context):
        """ Get the active image for painting """
        active_slot = context.object.active_material.paint_active_slot
        return context.object.active_material.texture_paint_images[active_slot]

    def get_brush_size(self, context: bpy.types.Context):
        """ Get the active brush size """
        return context.tool_settings.unified_paint_settings.size

    def get_brush_color(self, context: bpy.types.Context):
        """ Get the active brush size """
        return context.tool_settings.image_paint.brush.color

    def get_ray(self, context: bpy.types.Context, x, y):
        """ Get the ray under the mouse cursor """
        region = context.region
        rv3d = context.region_data
        coord = x-region.x,y-region.y

        # get the ray from the viewport and mouse
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        return ray_origin,ray_direction

    def ray_cast_on_object(self, ray_origin, ray_direction):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = self.matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_direction_obj = matrix_inv.to_3x3() @ ray_direction

        # cast the ray
        obj = self.paint_mesh.object
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
        if success:
            return location, normal, face_index
        else:
            return None, None, None
