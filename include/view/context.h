#ifndef VIEW_CONTEXT_H
#define VIEW_CONTEXT_H

#include <Python.h>
#include <view/backport.h>

extern PyTypeObject ContextType;
PyObject* context_from_data(PyObject* scope);

#endif
