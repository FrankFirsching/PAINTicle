# A particles shooter class

from bpy_extras import view3d_utils
import bpy
import mathutils

class Particles:
    """ A class managing the particle system for the paint operator """
    def __init__(self):
        pass

    def shoot(self, context, event):
        """ Shoot particles and paint them """
        ray_origin,ray_direction = self.get_ray(context,
                                             event.mouse_x, event.mouse_y)
        
        paint_object = context.active_object
        matrix = paint_object.matrix_world.copy()
        location,normal,face_index = self.ray_cast_on_object(paint_object,
                                                             matrix,
                                                             ray_origin,
                                                             ray_direction)

        if location != None:
            paint_image = self.get_active_image(context)
            active_brush = self.get_active_brush(context)
            self.paint_particles(location, normal, face_index, paint_object, paint_image, active_brush.color)

    def get_active_image(self, context):
        """ Get the active image for painting """
        active_slot = context.object.active_material.paint_active_slot
        return context.object.active_material.texture_paint_images[active_slot]

    def get_active_brush(self, context):
        """ Get the active brush """
        return context.tool_settings.image_paint.brush

    def get_ray(self, context, x, y):
        """ Get the ray under the mouse cursor """
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = x-region.x,y-region.y

        # get the ray from the viewport and mouse
        ray_direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        return ray_origin,ray_direction

    def ray_cast_on_object(self, obj, matrix, ray_origin, ray_direction):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_direction_obj = matrix_inv.to_3x3() @ ray_direction

        # cast the ray
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

        if success:
            return location, normal, face_index
        else:
            return None, None, None

    def paint_particles(self, location, normal, face_index, paint_object, paint_image, color):
        """ After ray casting paint onto the hit location """
        mesh = paint_object.data
        if (not mesh.polygons) or (face_index >= len(mesh.polygons)):
            print("ERROR: Can't find face")
            return
        face = mesh.polygons[face_index]
        points = [mesh.vertices[vi].co for vi in face.vertices]

        uvMap = mesh.uv_layers['UVMap']
        uvMapIndices = face.loop_indices



        #uvs = [mesh.uvs[vi].co for vi in face.vertices]
        tessellated = mathutils.geometry.tessellate_polygon([points])
        for tri in tessellated:
            p0 = points[tri[0]]
            p1 = points[tri[1]]
            p2 = points[tri[2]]
            uv0 = uvMap.data[uvMapIndices[tri[0]]].uv.copy()
            uv0.resize_3d()
            uv1 = uvMap.data[uvMapIndices[tri[1]]].uv.copy()
            uv1.resize_3d()
            uv2 = uvMap.data[uvMapIndices[tri[2]]].uv.copy()
            uv2.resize_3d()
            location_uv=None
            if mathutils.geometry.intersect_point_tri(location,p0,p1,p2):
                location_uv = mathutils.geometry.\
                    barycentric_transform(location, p0,p1,p2, uv0, uv1, uv2)
                self.paint_particle(location_uv, mesh, paint_image, color)
    
    def set_pixel(self, image, x,y, color):
        """ Set a single pixel in the image """
        image_size = image.size
        pixels = image.pixels
        indx = (x+y*image_size[0])*4
        pixels[indx+0] = color[0]
        pixels[indx+1] = color[1]
        pixels[indx+2] = color[2]
        
    def paint_particle(self, uv, mesh, paint_image, color):
        """ Paint a single particle """
        image_size = paint_image.size
        pixels = paint_image.pixels
        x = int(uv[0]*image_size[0])
        y = int(uv[1]*image_size[1])
        indx = (x+y*image_size[0])*4
        self.set_pixel(paint_image, x,y, color)
        