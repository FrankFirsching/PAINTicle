import bpy

class ParticlePaintPanel:
    """ A mixin class for the concrete panels below """
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_options = {"DEFAULT_CLOSED"}

class ParticlePaintMainPanel(ParticlePaintPanel, bpy.types.Panel):
    """ The main particle paint panel, shown in the tool settings """
    bl_label = "Particle Paint"
    bl_idname = "PARTICLE_PAINT_PT_main_panel"
    bl_context = "imagepaint"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        settings = context.scene.particle_paint_settings
        layout.prop(settings, "particle_size")
        layout.prop(settings, "particle_size_random")
        layout.prop(settings, "max_age")
        layout.prop(settings, "max_age_random")
        layout.prop(settings, "color_random")
        layout.prop(settings, "stop_painting_on_mouse_release")

class ParticlePaintPhysicsPanel(ParticlePaintPanel, bpy.types.Panel):
    """ A sub panel grouping the physics settings """
    bl_label = "Physics"
    bl_idname = "PARTICLE_PAINT_PT_physics_panel"
    bl_parent_id = "PARTICLE_PAINT_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        physics = context.scene.particle_paint_settings.physics
        layout.prop(physics, "gravity")
