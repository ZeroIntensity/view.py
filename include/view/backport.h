#ifndef VIEW_BACKPORT_H
#define VIEW_BACKPORT_H

#include <Python.h>

#if PY_MAJOR_VERSION != 3
#error "this file assumes python 3"
#endif

#ifndef _PyObject_Vectorcall
static PyObject *
_PyObject_VectorcallBackport(
    PyObject *obj,
    PyObject **args,
    size_t nargsf,
    PyObject *kwargs
)
{
    assert(obj != NULL);
    assert(nargsf >= 0);
    PyObject *tuple = PyTuple_New(nargsf);
    if (tuple == NULL)
    {
        return NULL;
    }
    for (size_t i = 0; i < nargsf; ++i)
    {
        Py_INCREF(args[i]);
        PyTuple_SET_ITEM(tuple, i, args[i]);
    }
    PyObject *o = PyObject_Call(obj, tuple, kwargs);
    Py_DECREF(tuple);
    return o;
}

#define PyObject_CallNoArgs(o) PyObject_CallObject(o, NULL)
#define PyObject_Vectorcall _PyObject_VectorcallBackport
#define PyObject_VectorcallDict _PyObject_FastCallDict
#endif

#ifndef Py_NewRef
static PyObject *
Py_NewRef(PyObject *o)
{
    assert(o != NULL);
    Py_INCREF(o);
    return o;
}

#endif

#ifndef Py_XNewRef
static PyObject *
Py_XNewRef(PyObject *o)
{
    Py_XINCREF(o);
    return o;
}

#endif

#ifndef Py_IS_TYPE
#define Py_IS_TYPE(o, type) (Py_TYPE(o) == type)
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

#if PY_VERSION_HEX < 0x030c0000
static PyObject *
PyErr_GetRaisedException(void)
{
    PyObject *type, *val, *tb;
    PyErr_Fetch(&type, &val, &tb);
    PyErr_NormalizeException(&type, &val, &tb);
    Py_XDECREF(type);
    Py_XDECREF(tb);
    // technically some entry in the traceback might be lost; ignore that
    assert(val != NULL);
    return val;
}

static void
PyErr_SetRaisedException(PyObject *err)
{
    PyErr_Restore((PyObject *) Py_TYPE(err), err, NULL);
}

#endif

#endif
