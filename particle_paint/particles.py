# A particles shooter class

from bpy_extras import view3d_utils
import bpy
import mathutils

import math
import random

from . import physics
from . import trianglemesh
from .utils import Error
from . import particle_painter_gpu


class Particle:
    nextParticleId = 0
    rnd = random.Random()

    """ A single particle """
    def __init__(self, location, tri_index, paint_mesh, particle_settings):
        self.id = Particle.nextParticleId
        Particle.nextParticleId += 1
        self.location = location
        self.tri_index = tri_index
        self.speed = mathutils.Vector((0, 0, 0))
        self.mass = 50
        self.barycentric = mathutils.Vector((0, 0, 0))
        self.normal = mathutils.Vector((0, 0, 0))
        self.uv = mathutils.Vector((0, 0))
        
        rnd = Particle.rnd
        random_size = rnd.uniform(-particle_settings.particle_size_random,
                                   particle_settings.particle_size_random)
        self.particle_size = particle_settings.particle_size+random_size

        self.age = 0.0
        random_age = rnd.uniform(-particle_settings.max_age_random,
                                  particle_settings.max_age_random)
        self.max_age = particle_settings.max_age + random_age

        self.colorOffset = [0, 0, 0]
        colRand = particle_settings.color_random
        self.colorOffset[0] = rnd.uniform(-colRand.h, colRand.h)
        self.colorOffset[1] = rnd.uniform(-colRand.s, colRand.s)
        self.colorOffset[2] = rnd.uniform(-colRand.v, colRand.v)
        
        self.update_location_dependent_properties(paint_mesh)

    def move(self, physics, paint_mesh, deltaT):
        orthoForce = physics.gravityNormalized.dot(self.normal) * self.normal
        planeForce = physics.gravity - orthoForce
        self.speed += deltaT*planeForce/self.mass
        self.location += deltaT*self.speed
        self.age += deltaT
        self.update_location_dependent_properties(paint_mesh)

    def get_uv(self):
        return self.uv

    def update_location_dependent_properties(self, paint_mesh):
        self.project_back_to_triangle(paint_mesh)
        self.barycentric = paint_mesh.barycentrics(self.location, self.tri_index)

        mesh = paint_mesh.mesh
        tri = mesh.loop_triangles[self.tri_index]
        n = [mesh.vertices[i].normal for i in tri.vertices]

        uvMap = mesh.uv_layers.active
        uv = [uvMap.data[i].uv.copy() for i in tri.loops]

        if all(coord > 0 for coord in self.barycentric):
            # If we're within the triangle...
            uv[0].resize_3d()
            uv[1].resize_3d()
            uv[2].resize_3d()
            uvx = paint_mesh.barycentrics(self.location, self.tri_index,
                                          uv[0], uv[1], uv[2])
            self.uv = uvx.resized(2)
            self.normal = paint_mesh.barycentrics(self.location, self.tri_index,
                                                  n[0], n[1], n[2])
            self.normal.normalize()

    def project_back_to_triangle(self, paint_mesh):
        # Put the particle back to the triangle surface
        if True:  # Use triangle neighbor info movement
            new_location = \
                paint_mesh.project_point_to_triangle(self.location, self.tri_index)
            
            new_location, new_tri_index = \
                paint_mesh.move_over_triangle_boundaries(self.location, new_location, self.tri_index)
            self.location = new_location
            self.tri_index = new_tri_index
        else:
            result, location, normal, index = paint_mesh.object.closest_point_on_mesh(self.location)
            if result:
                self.location = location
                self.tri_index = paint_mesh.triangle_for_point_on_poly(location, index)

    def generateStroke(self, context, overallStrength):
        region = context['region']
        mousePos = self.uvToMousePos(region, self.uv)
        alpha = 1 - self.age / self.max_age
        return { "name":"ParticleStroke",
                 "is_start":False,
                 "location":self.location,
                 "mouse":mousePos,
                 "pen_flip":False,
                 "pressure":alpha*overallStrength,
                 "size":self.particle_size,
                 "time":0,
                 "mouse_event": mousePos,
                 "x_tilt": 0,
                 "y_tilt": 0 }

    def uvToMousePos(self, region, uv):
        """ Calculating a pixel position on the Image Editor for given UV
            coordinate. We're usingthe region_to_view function, since it's more
            accurate, as view_to_region rounds to integers. """
        diffLength = min(region.width, region.height)
        view00 = region.view2d.region_to_view(0, 0)
        view11 = region.view2d.region_to_view(diffLength, diffLength)
        viewDiff = (view11[0]-view00[0], view11[1]-view00[1])
        origin = (-view00[0]/viewDiff[0]*diffLength, -view00[1]/viewDiff[1]*diffLength)
        upperLeft = ((1-view00[0])/viewDiff[0]*diffLength, (1-view00[1])/viewDiff[1]*diffLength)
        scale = (upperLeft[0]-origin[0], upperLeft[1]-origin[1])
        return [uv[0]*scale[0]+origin[0], uv[1]*scale[1]+origin[1]]

class Particles:
    """ A class managing the particle system for the paint operator """
    def __init__(self, context):
        self.rnd = random.Random()
        self.paint_mesh = trianglemesh.TriangleMesh(context.active_object)
        self.matrix = self.paint_mesh.object.matrix_world.copy()
        self.particles = []
        self.painter = particle_painter_gpu.ParticlePainterGPU(context)

    def numParticles(self):
        """ Return the number of simulated particles """
        return len(self.particles)
    
    def shoot(self, context, event, particle_settings):
        """ Shoot particles and paint them """
        paint_size = self.get_brush_size(context)
        angle = 2*math.pi*self.rnd.random()
        distance = paint_size*self.rnd.random()
        offset_x = math.cos(angle)*distance
        offset_y = math.sin(angle)*distance
        ray_origin,ray_direction = self.get_ray(context,
                                                event.mouse_x+offset_x,
                                                event.mouse_y+offset_y)
        
        location,normal,face_index = self.ray_cast_on_object(ray_origin,
                                                             ray_direction)
        if location != None:
            tri_index = self.paint_mesh.triangle_for_point_on_poly(location, face_index)
            self.add_particle(Particle(location, tri_index, self.paint_mesh, particle_settings))
    
    def move_particles(self, physics, deltaT):
        """ Simulate gravity """
        for i in range(len(self.particles) - 1, -1, -1):
            p = self.particles[i]
            p.move(physics, self.paint_mesh, deltaT)
            if p.age > p.max_age:
                del self.particles[i]

    def paint_particles(self, context):
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

    def get_active_image(self, context):
        """ Get the active image for painting """
        active_slot = context.object.active_material.paint_active_slot
        return context.object.active_material.texture_paint_images[active_slot]

    def get_brush_size(self, context):
        """ Get the active brush size """
        return context.tool_settings.unified_paint_settings.size

    def get_ray(self, context, x, y):
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
