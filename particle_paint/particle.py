# A class representing a single particle

import array
import random

import mathutils


class Particle:
    """  A single particle. """

    nextParticleId = 0
    rnd = random.Random()

    """ A single particle """
    def __init__(self, location, tri_index, color, paint_mesh, particle_settings):
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

        colRand = particle_settings.color_random
        self.color = color.copy()
        self.color.h += rnd.uniform(-colRand.h, colRand.h)
        self.color.s += rnd.uniform(-colRand.s, colRand.s)
        self.color.v += rnd.uniform(-colRand.v, colRand.v)

        if paint_mesh is not None:
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

    def append_visual_properties(self, vbo_data: array.array):
        """ Append the particle's visual properties to the vbo data array.
            Order conforms to the Particle definition in the shader """
        vbo_data.extend(self.uv)
        vbo_data.append(self.particle_size)
        vbo_data.append(self.age)
        vbo_data.append(self.max_age)
        vbo_data.append(self.color.r)
        vbo_data.append(self.color.g)
        vbo_data.append(self.color.b)

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
