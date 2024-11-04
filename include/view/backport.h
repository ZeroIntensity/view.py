#ifndef VIEW_BACKPORT_H
#define VIEW_BACKPORT_H

#include <Python.h>

#if PY_MAJOR_VERSION != 3
#error "this file assumes python 3"
#endif

#ifndef _PyObject_Vectorcall
#define VIEW_NEEDS_VECTORCALL
PyObject * _PyObject_VectorcallBackport(
    PyObject *obj,
    PyObject **args,
    size_t nargsf,
    PyObject *kwargs
);

#define PyObject_CallNoArgs(o) PyObject_CallObject(o, NULL)
#define PyObject_Vectorcall _PyObject_VectorcallBackport
#define PyObject_VectorcallDict _PyObject_FastCallDict
#endif

#if PY_VERSION_HEX < 0x030c0000
PyObject * PyErr_GetRaisedException(void);
void PyErr_SetRaisedException(PyObject *err);
#endif

#ifndef Py_NewRef
#define VIEW_NEEDS_NEWREF
PyObject * Py_NewRef_Backport(PyObject *o);
#define Py_NewRef Py_NewRef_Backport
#endif

#ifndef Py_XNewRef
#define VIEW_NEEDS_XNEWREF
PyObject * Py_XNewRef_Backport(PyObject *o);
#define Py_XNewRef Py_XNewRef_Backport
#endif

#ifndef Py_IS_TYPE
#define Py_IS_TYPE(o, type) (Py_TYPE(o) == type)
#endif

#if PY_MINOR_VERSION == 8
#define PyObject_CallOneArg(func, val) \
        PyObject_Vectorcall(func, (PyObject *[]) { val }, 1, NULL)
#endif

#if PY_MINOR_VERSION < 13
static int
PyModule_Add(PyObject *module, const char *name, PyObject *value)
{
    if (value == NULL)
    {
        return -1;
    }
    if (PyModule_AddObject(module, name, value) < 0)
    {
        Py_DECREF(value);
        return -1;
    }
    return 0;
}

#endif

#endif
