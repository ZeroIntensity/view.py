#include <Python.h>
#include <view/view.h>

#define METHOD(name) { #name, name, METH_VARARGS, NULL }
#define METHOD_NOARGS(name) { #name, name, METH_NOARGS, NULL }

PyObject* test(PyObject* self, PyObject* args) {
    PyObject* o;
    if (!PyArg_ParseTuple(
        args,
        "O",
        &o
        )) return NULL;
    PyObject* awaitable = PyAwaitable_New();
    if (!awaitable) return NULL;

    if (PyAwaitable_AWAIT(
        awaitable,
        o
        ) < 0) return NULL;
    return awaitable;
}

static PyMethodDef methods[] = {
    METHOD(test),
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_view",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit__view() {
    PyObject* m = PyModule_Create(&module);

    if (PyModule_AddIntMacro(
        m,
        PASS_CTX
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    if (PyModule_AddIntMacro(
        m,
        USE_CACHE
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    if (
        (PyType_Ready(&PyAwaitable_Type) < 0) ||
        (PyType_Ready(&ViewAppType) < 0) ||
        (PyType_Ready(&_PyAwaitable_GenWrapper_Type) < 0)
    ) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&PyAwaitable_Type);


    if (PyModule_AddObject(
        m,
        "Awaitable",
        (PyObject*) &PyAwaitable_Type
        ) < 0) {
        Py_DECREF(&PyAwaitable_Type);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&ViewAppType);

    if (PyModule_AddObject(
        m,
        "ViewApp",
        (PyObject*) &ViewAppType
        ) < 0) {
        Py_DECREF(&ViewAppType);
        Py_DECREF(&PyAwaitable_Type);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&_PyAwaitable_GenWrapper_Type);
    if (PyModule_AddObject(
        m,
        "_GenWrapper",
        (PyObject*) &_PyAwaitable_GenWrapper_Type
        ) < 0) {
        Py_DECREF(&ViewAppType);
        Py_DECREF(&PyAwaitable_Type);
        Py_DECREF(&_PyAwaitable_GenWrapper_Type);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
