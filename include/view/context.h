#ifndef VIEW_CONTEXT_H
#define VIEW_CONTEXT_H

#include <Python.h>
#include <view/backport.h>

extern PyTypeObject ContextType;
PyObject* Context_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);

#endif
