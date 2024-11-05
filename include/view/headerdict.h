#ifndef VIEW_HEADERDICT_H
#define VIEW_HEADERDICT_H

#include <Python.h> // PyObject, PyTypeObject

extern PyTypeObject ViewHeaderDictType;
PyObject * ViewHeaderDict_FromList(PyObject *list, PyObject *cookies);

#endif
