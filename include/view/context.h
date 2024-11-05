#ifndef VIEW_CONTEXT_H
#define VIEW_CONTEXT_H

#include <Python.h> // PyObject, PyTypeObject

extern PyTypeObject ViewContext_Type;
PyObject * ViewContext_FromData(PyObject *app, PyObject *scope);

#endif
