# Utility classes


class Error(Exception):
    """ Base class for errors in this module """
    pass


def lerp(t, a, b):
    """ Perform a linear interpolation between a and b using factor t """
    return (1-t)*a + t*b


def matrix_to_tuple(m):
    """ Convert given blender matrix into a tuple to be usable by moderngl """
    return (m[0][0], m[1][0], m[2][0], m[3][0],
            m[0][1], m[1][1], m[2][1], m[3][1],
            m[0][2], m[1][2], m[2][2], m[3][2],
            m[0][3], m[1][3], m[2][3], m[3][3])
