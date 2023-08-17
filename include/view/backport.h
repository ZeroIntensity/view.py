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
static PyObject* _PyObject_VectorcallBackport(PyObject* obj,
                                              const PyObject** args,
                                              size_t nargsf, PyObject* kwargs) {
    PyObject* tuple = PyTuple_New(nargsf);
    if (!tuple) return NULL;
    for (int i = 0; i < nargsf; i++) {
        Py_INCREF(args[i]);
        PyTuple_SET_ITEM(
            tuple,
            i,
            args[i]
        );
    }
    PyObject* o = PyObject_Call(
        obj,
        tuple,
        kwargs
    );
    Py_DECREF(tuple);
    return o;
}
#define PyObject_Vectorcall _PyObject_VectorcallBackport
#define PyObject_VectorcallDict _PyObject_FastCallDict
#endif

#ifndef Py_IS_TYPE
#define Py_IS_TYPE(p, type) (Py_TYPE(o) == type)
#endif

#endif
