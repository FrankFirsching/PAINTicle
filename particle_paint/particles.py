# A particles shooter class

from bpy_extras import view3d_utils
import bpy
import mathutils

import math
import random

import particle_paint.physics
import particle_paint.trianglemesh
import particle_paint.native

class Error(Exception):
    """ Base class for errors in this module """
    pass

class Particle:
    """ A single particle """
    def __init__(self, location, normal, face_index, particle_settings):
        self.location = location
        self.normal = normal.normalized()
        self.face_index = face_index
        self.speed = mathutils.Vector((0,0,0))
        self.mass = 50
        self.barycentric = mathutils.Vector((0,0,0))
        self.uv=mathutils.Vector((0,0,0))
        self.rnd = random.Random()
        
        random_size = self.rnd.uniform(-particle_settings.particle_size_random,
                                        particle_settings.particle_size_random)
        self.particle_size = particle_settings.particle_size+random_size

        self.age = 0.0
        random_age = self.rnd.uniform(-particle_settings.max_age_random,
                                       particle_settings.max_age_random)
        self.max_age = particle_settings.max_age + random_age

    def move(self, physics, paint_mesh, deltaT):
        orthoForce = physics.gravityNormalized.dot(self.normal) * self.normal
        planeForce = physics.gravity - orthoForce
        self.speed += deltaT*planeForce/self.mass
        self.location += deltaT*self.speed
        self.age += deltaT
        self.update_uv(paint_mesh)

    def get_uv(self):
        return self.uv

    def update_uv(self, paint_mesh, whenOutsideSearchNewFace=True):
        mesh = paint_mesh.mesh
        if self.face_index >= len(mesh.polygons):
            raise Error("ERROR: Particle is lying on a wrong face")

        #face = mesh.polygons[self.face_index]

        uvMap = mesh.uv_layers.active # ['UVMap']

        tessellated = paint_mesh.poly_to_tri[self.face_index]
        for tri_index in tessellated:
            tri = mesh.loop_triangles[tri_index]
            p = [mesh.vertices[i].co  for i in tri.vertices]
            uv = [uvMap.data[i].uv.copy() for i in tri.loops]
            uv[0].resize_3d()
            uv[1].resize_3d()
            uv[2].resize_3d()
            if mathutils.geometry.intersect_point_tri(self.location,p[0],p[1],p[2]):
                self.uv = mathutils.geometry.\
                    barycentric_transform(self.location, p[0],p[1],p[2], uv[0], uv[1], uv[2])
                return
        # Here we haven't found any uv, so we probably have left the face
        if whenOutsideSearchNewFace:
            result, location, normal, index = paint_mesh.object.closest_point_on_mesh(self.location)
            if result:
                self.location = location
                self.normal = normal
                self.face_index = index
                self.update_uv(paint_mesh, False)

    def generateStroke(self, context):
        region = context['region']
        mousePos = self.uvToMousePos(region, self.uv)
        alpha = 1 - self.age / self.max_age
        return {"name":"ParticleStroke",
                    "is_start":False,
                    "location":self.location,
                    "mouse":mousePos,
                    "pen_flip":False,
                    "pressure":alpha,
                    "size":self.particle_size,
                    "time":0 }

    def uvToMousePos(self, region, uv):
        """ Calculating a pixel position on the Image Editor for given UV
            coordinate. We're usingthe region_to_view function, since it's more
            accurate, as view_to_region rounds to integers. """
        diffLength=min(region.width, region.height)
        view00 = region.view2d.region_to_view(0, 0)
        view11 = region.view2d.region_to_view(diffLength, diffLength)
        viewDiff = ( view11[0]-view00[0], view11[1]-view00[1] )
        origin = ( -view00[0]/viewDiff[0]*diffLength,-view00[1]/viewDiff[1]*diffLength )
        upperLeft = ( (1-view00[0])/viewDiff[0]*diffLength,(1-view00[1])/viewDiff[1]*diffLength )
        scale = ( upperLeft[0]-origin[0], upperLeft[1]-origin[1] )
        return [ uv[0]*scale[0]+origin[0], uv[1]*scale[1]+origin[1] ]

class Particles:
    """ A class managing the particle system for the paint operator """
    def __init__(self, context):
        pass
        self.rnd = random.Random()
        self.paint_mesh = particle_paint.trianglemesh.TriangleMesh(context.active_object)
        self.matrix = self.paint_mesh.object.matrix_world.copy()
        self.paint_image = None
        self.paint_pixels = None
        self.particles = []
        self.img_painting_in_float = True
        self.fakeUvContext=self.createFakeUvContext(context)

    def createFakeUvContext(self, context):
        """ We fake a Uv context using a square aspect ratio, where we can paint
            into """
        screen = context.screen
        fakedContext = context.copy()

        # Update the context 
        for area in screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        fakedContext = {'region': region, 'area': area}

        return fakedContext
    
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
            self.add_particle(Particle(location, normal, face_index, particle_settings))
    
    def move_particles(self, physics, deltaT):
        """ Simulate gravity """
        for i in range(len(self.particles) - 1, -1, -1):
            p = self.particles[i]
            p.move(physics, self.paint_mesh, deltaT)
            if p.age > p.max_age:
                del self.particles[i]

    def paint_particles(self, context):
        """ Paint all particles into the texture """
        strokes = [p.generateStroke(self.fakeUvContext) for p in self.particles]
        bpy.ops.paint.image_paint(self.fakeUvContext, stroke=strokes)

    def clear_particles(self):
        """ Start with an empty set of particles """
        self.particles = []

    def add_particle(self, particle):
        """ Add a single particle """
        self.particles.append(particle)

    def get_active_image(self, context):
        """ Get the active image for painting """
        active_slot = context.object.active_material.paint_active_slot
        return context.object.active_material.texture_paint_images[active_slot]

    def get_active_brush(self, context):
        """ Get the active brush """
        return context.tool_settings.image_paint.brush

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
