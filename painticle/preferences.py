from bpy.props import IntProperty
from bpy.types import PropertyGroup


id = __package__


def get_instance(context):
    """ Gets the blender managed instance of these preferences """
    global id
    # Unfortunately we need to reference a member of the preferences panel, since
    # blender doesn't separate UI and data for the preferences.
    return context.preferences.addons[id].preferences.painticle


class Preferences(PropertyGroup):
    """ The preferences object for the painticle add-on """
    preview_threshold_edge: IntProperty(name="Preview Mode Threshold",
                                        description="Performance option:\n"+
                                                    "Specifies the size of a square texture, that represents the " +
                                                    "largest image size still possible to simulate without falling " +
                                                    "back to preview mode.",
                                        default=1024, min=0, soft_min=0, soft_max=4096,
                                        options=set())
