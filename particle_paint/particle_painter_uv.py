# The UV editor base particle painter

# <pep8 compliant>

from . import particle_painter

import bpy


class ParticlePainterUV(particle_painter.ParticlePainter):
    """ This particle painter is abusing the UV editor to draw the 
        particles. """

    def __init__(self, context: bpy.types.Context):
        super().__init__(context)
        self.fakeUvContext = self.createFakeUvContext(context)

    def shutdown(self):
        # Nothing to be done for this painter
        pass

    def draw(self, particles):
        brush = self.get_active_brush()
        strength = brush.strength
        settings = self.get_particle_settings()
        oldBrushColor = brush.color.copy()
        for p in particles:
            stroke = [p.generateStroke(self.fakeUvContext, strength, settings)]
            brush.color = p.color
            bpy.ops.paint.image_paint(self.fakeUvContext, stroke=stroke)
        brush.color = oldBrushColor

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
