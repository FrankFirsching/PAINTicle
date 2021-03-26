# Utility classes


class Error(Exception):
    """ Base class for errors in this module """
    pass


def lerp(t, a, b):
    """ Perform a linear interpolation between a and b using factor t """
    return (1-t)*a + t*b