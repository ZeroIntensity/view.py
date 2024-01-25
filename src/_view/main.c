#include <Python.h>
#include <view/view.h>

// i hate my formatter

#define METHOD(name)                                                           \
  {                                                                            \
#name, name, METH_VARARGS, NULL                                            \
  }
#define METHOD_NOARGS(name)                                                    \
  {                                                                            \
#name, name, METH_NOARGS, NULL                                             \
  }



static PyMethodDef methods[] = {{NULL, NULL, 0, NULL}};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "_view", NULL, -1,
                                    methods};
PyObject* ip_address = NULL;

void view_fatal(
    const char* message,
    const char* where,
    const char* func,
    int lineno
) {
    fprintf(
        stderr,
        "_view FATAL ERROR at [%s:%d] in %s: %s",
        where,
        lineno,
        func,
        message
    );
    fputs(
        "Please report this at https://github.com/ZeroIntensity/view.py/issues",
        stderr
    );
    Py_FatalError("view.py core died");
};



PyMODINIT_FUNC PyInit__view() {
    PyObject* m = PyModule_Create(&module);

    if ((PyType_Ready(&PyAwaitable_Type) < 0) ||
        (PyType_Ready(&ViewAppType) < 0) ||
        (PyType_Ready(&_PyAwaitable_GenWrapper_Type) < 0) || (PyType_Ready(
            &ContextType) < 0) || (PyType_Ready(&TCPublicType) < 0)) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&PyAwaitable_Type);

    if (PyModule_AddObject(
        m,
        "Awaitable",
        (PyObject*) &PyAwaitable_Type
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&ViewAppType);

    if (PyModule_AddObject(
        m,
        "ViewApp",
        (PyObject*) &ViewAppType
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&_PyAwaitable_GenWrapper_Type);
    if (PyModule_AddObject(
        m,
        "_GenWrapper",
        (PyObject*) &_PyAwaitable_GenWrapper_Type
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&ContextType);
    if (PyModule_AddObject(m, "Context", (PyObject*) &ContextType) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&TCPublicType);
    if (PyModule_AddObject(m, "TCPublic", (PyObject*) &TCPublicType) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    PyObject* ipaddress_mod = PyImport_ImportModule("ipaddress");
    if (!ipaddress_mod) {
        Py_DECREF(m);
        return NULL;
    }

    ip_address = PyObject_GetAttrString(ipaddress_mod, "ip_address");
    if (!ip_address) {
        Py_DECREF(m);
        Py_DECREF(ipaddress_mod);
        return NULL;
    }
    Py_DECREF(ipaddress_mod);

    return m;
}
