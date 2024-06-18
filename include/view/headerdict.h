#ifndef VIEW_HEADERDICT_H
#define VIEW_HEADERDICT_H

#include <Python.h> // PyObject, PyTypeObject

extern PyTypeObject HeaderDictType;
PyObject* headerdict_from_list(PyObject* list);

#endif
