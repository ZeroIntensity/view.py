#ifndef VIEW_CONTEXT_H
#define VIEW_CONTEXT_H

#include <Python.h>
#include <view/backport.h>

extern PyTypeObject ContextType;
PyObject* Context_new(PyTypeObject* type, PyObject* args, PyObject* kwargs);
PyObject* handle_route_data(int data, PyObject* scope);

#endif
