# Generic blender gpu addons

import gpu

def image_sizes(image):
    """ Thus function shall return all images sizes of all UDIM tiles. However
        currently blender doesn't allow access to the tiles, except their names.
        So we can only work with untiles images """
    return [image.size]

def max_image_size(image):
    """ Thus function shall return the combined maximum images size of all UDIM tiles. However
        currently blender doesn't allow access to the tiles, except their names.
        So we can only work with untiles images """
    sizes = image_sizes(image)
    width = max([s[0] for s in sizes])
    height = max([s[1] for s in sizes])
    return width, height

def gpu_buffer_for_image(image):
    size = max_image_size(image)
    return gpu.types.GPUOffScreen(size[0], size[1])
