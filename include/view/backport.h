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

#ifndef _PyObject_Vectorcall
#define PyObject_CallNoArgs(o) PyObject_CallObject( \
    o, \
    NULL \
)
#define PyObject_Vectorcall _PyObject_Vectorcall
#define PyObject_VectorcallDict _PyObject_FastCallDict
#endif

#endif
