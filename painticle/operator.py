# This file is part of PAINTicle.
#
# PAINTicle is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PAINTicle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PAINTicle.  If not, see <http://www.gnu.org/licenses/>.

# <pep8 compliant>

import bpy
from mathutils import Vector

import cProfile
import pstats
import io
import time

import painticle.particles


# This class is the blender operator interface. It cares about mouse and pen
# handling. The real drawing is done in a different module: particles.
# See there for the real painting logic.
class PaintOperator(bpy.types.Operator):
    """Paint on the object using particles"""
    bl_idname = "view3d.painticle"
    bl_label = "PAINTicle"
    # bl_options = {'REGISTER', 'UNDO', 'UNDO_GROUPED'}
    bl_undo_group = "ParticlePaint"

    def __init__(self):
        """ Constructor """
        self._timer = None
        self.lastcall = 0
        self.pr = None

    @classmethod
    def poll(cls, context):
        # TODO: Check when to allow activation of operator
        return True

    def modal(self, context, event):
        """ Callback, if some event was happening """

        mouseOutsideOfArea = self.isMouseOutsideOfArea(context.area, event)
        if not self._left_mouse_pressed and mouseOutsideOfArea and event.type != 'TIMER':
            # Ignore everything, if not painting and outside
            return {'PASS_THROUGH'}

        if event.type == 'MOUSEMOVE':
            if self._left_mouse_pressed:
                # Keep the tool running
                return {'RUNNING_MODAL'}
        elif event.type == 'TIMER':
            settings = context.scene.painticle_settings
            currenttime = time.time_ns()
            delta_t = self.calc_time_step(currenttime, settings.physics.max_time_step)
            self.lastcall = currenttime
            if self._left_mouse_pressed:
                self._particles.shoot(context, event, delta_t, settings)
            self._particles.move_particles(settings.physics, delta_t)
            self._particles.paint_particles(delta_t)
            if not settings.stop_painting_on_mouse_release and not self._left_mouse_pressed:
                if self._particles.numParticles() == 0:
                    self.setTimer(context, False)

        elif event.type == 'LEFTMOUSE':
            # Track the mouse press state
            self._left_mouse_pressed = (event.value == "PRESS")
            if self._left_mouse_pressed:
                self.startProfile()
                self.setTimer(context, True)
                self.lastcall = time.time_ns()
                self._particles.clear_particles()
            else:
                settings = context.scene.painticle_settings
                if settings.stop_painting_on_mouse_release:
                    self.setTimer(context, False)
                self.endProfile()

            return {'RUNNING_MODAL'}

        elif event.type == 'U':
            if event.value == 'RELEASE':
                self._particles.undo_last_paint()
        elif event.type == 'ESC':
            # We end the tool with a right click
            context.area.header_text_set(None)
            self.setTimer(context, False)
            self._particles = None
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def calc_time_step(self, currenttime: float, max_time_step: float):
        delta_t = 0
        if self.lastcall != 0:
            # unit of given time is nanosecons. time_step is seconds.
            delta_t = (currenttime - self.lastcall) * 1e-9
        delta_t = min(max_time_step, delta_t)
        return delta_t

    def setTimer(self, context, onOff):
        wm = context.window_manager
        if self._timer is not None:  # Remove a potentially active timer
            wm.event_timer_remove(self._timer)
        if onOff:
            self._timer = wm.event_timer_add(0.01, window=context.window)
        else:
            self._timer = None

    def startProfile(self):
        if self.pr is None:
            return
            self.pr = cProfile.Profile()
            self.pr.enable()

    def endProfile(self):
        if self.pr is not None:
            self.pr.disable()
            s = io.StringIO()
            # sortby = pstats.SortKey.CUMULATIVE
            sortby = 'tottime'
            ps = pstats.Stats(self.pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())
            self.pr = None

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            # Move out of a potential camera view into normal perspective one, so we
            # don't risk changing the camera, if it's locked to the view.
            v3d = context.space_data
            rv3d = v3d.region_3d
            if rv3d.view_perspective == 'CAMERA':
                rv3d.view_perspective = 'PERSP'

            self._left_mouse_pressed = False
            self._particles = painticle.particles.Particles(context)

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
