#include <Python.h>

#include "paint.h"

static PyMethodDef nativePaintMethods[] = {
    {"paint",  paint, METH_VARARGS, "Paint the particles."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef nativePaintModule = {
    PyModuleDef_HEAD_INIT,
    "native",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    nativePaintMethods
};

PyMODINIT_FUNC PyInit_native(void)
{
    return PyModule_Create(&nativePaintModule);
}