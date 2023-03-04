#ifndef VIEW_BACKPORT_H
#define VIEW_BACKPORT_H

#include <Python.h>

#ifndef Py_NewRef
static inline PyObject* Py_NewRef(PyObject* o) {
    Py_INCREF(o);
    return o;
}
#endif

#ifndef Py_XNewRef
static inline PyObject* Py_XNewRef(PyObject* o) {
    Py_XINCREF(o);
    return o;
}
#endif

#if PY_MINOR_VERSION < 9
#define PyObject_CallNoArgs(o) PyObject_CallObject( \
    o, \
    NULL \
)
#endif

#endif
