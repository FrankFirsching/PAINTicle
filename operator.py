import bpy
from mathutils import Vector
from bpy.props import FloatVectorProperty

import particle_paint.particles


# This class is the blender operator interface. It cares about mouse and pen
# handling. The real drawing is done in a different module: particles.
# See there for the real painting logic.
class PaintOperator(bpy.types.Operator):
    """Paint on the object using particles"""
    bl_idname = "view3d.particle_paint"
    bl_label = "Particle Paint"

    def __init__(self):
        """ Constructor """
        self._timer = None
    
    def modal(self, context, event):
        """ Callback, if some event was happening """

        mouseOutsideOfArea = self.isMouseOutsideOfArea(context.area, event)
        if not self._left_mouse_pressed and mouseOutsideOfArea:
            # Ignore everything, if not painting and outside
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            if self._left_mouse_pressed:
                # Shoot particle and paint
                self._particles.shoot(context, event)
                return {'RUNNING_MODAL'}
        elif event.type == 'TIMER':
            if self._left_mouse_pressed:
                self._particles.shoot(context, event)
                self._particles.move_particles()
                self._particles.paint_particles(context)
        elif event.type == 'LEFTMOUSE':
            # Track the mouse press state
            self._left_mouse_pressed = (event.value=="PRESS")
            wm = context.window_manager
            if self._timer!=None: # Remove a potention other timer
                wm.event_timer_remove(self._timer)
                self._timer = None
            if self._left_mouse_pressed:
                self._timer = wm.event_timer_add(0.1, window=context.window)
                self._particles.clear_particles()
            return {'RUNNING_MODAL'}

        elif event.type in {'ESC'}:
            # We end the tool with a right click
            context.area.header_text_set(None)
            if self._timer!=None: # Remove a potential active timer
                wm.event_timer_remove(self._timer)
                self._timer = None
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            v3d = context.space_data
            rv3d = v3d.region_3d

            if rv3d.view_perspective == 'CAMERA':
                rv3d.view_perspective = 'PERSP'

            self._left_mouse_pressed = False
            self._particles = particle_paint.particles.Particles(context)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

    def isMouseOutsideOfArea(self, area, event):
        return area.x > event.mouse_x or \
               area.y > event.mouse_y or \
               area.x+area.width < event.mouse_x or \
               area.y+area.height < event.mouse_y
