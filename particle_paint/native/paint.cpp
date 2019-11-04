#include "paint.h"

PyObject* paint(PyObject *self, PyObject *args)
{
    // Args are:
    // self.paint_image, self.paint_pixels,
    // self.particles, self.max_age,
    // active_brush.color

    return PyLong_FromLong(42);
}