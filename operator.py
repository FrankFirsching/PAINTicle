import bpy
from mathutils import Vector
from bpy.props import FloatVectorProperty

import particle_paint.particles


# This class is the blender operator interface. It cares about mouse and pen
# handling. The real drawing is done in a different module: particles.
# See there for the real painting logic.
class PaintOperator(bpy.types.Operator):
    """Paint on the object using particles"""
    bl_idname = "view3d.modal_operator"
    bl_label = "Particle Paint"

    def modal(self, context, event):
        v3d = context.space_data
        rv3d = v3d.region_3d

        if event.type == 'MOUSEMOVE':
            if self._left_mouse_pressed:
                # Shoot particle and paint
                self._particles.shoot(context, event)

        elif event.type == 'LEFTMOUSE':
            # Track the mouse press state
            self._left_mouse_pressed = (event.value=="PRESS")
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # We end the tool with a right click
            context.area.header_text_set(None)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        if context.space_data.type == 'VIEW_3D':
            v3d = context.space_data
            rv3d = v3d.region_3d

            if rv3d.view_perspective == 'CAMERA':
                rv3d.view_perspective = 'PERSP'

            self._left_mouse_pressed = False
            self._particles = particle_paint.particles.Particles()

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}