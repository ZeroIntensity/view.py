#ifndef VIEW_CONTEXT_H
#define VIEW_CONTEXT_H

#include <Python.h> // PyObject, PyTypeObject

extern PyTypeObject ContextType;
PyObject * View_context_from_data(PyObject *app, PyObject *scope);

#endif
