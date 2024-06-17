#include <Python.h>
#include <signal.h>

#include <view/app.h>
#include <view/awaitable.h>
#include <view/context.h>
#include <view/headerdict.h>
#include <view/typecodes.h>
#include <view/ws.h>
#include <view/view.h>

PyObject* route_log = NULL;
PyObject* route_warn = NULL;
PyObject* ip_address = NULL;
PyObject* invalid_status_error = NULL;
PyObject* ws_cls = NULL;
PyObject* ws_disconnect_err = NULL;
PyObject* ws_err_cls = NULL;

static PyObject* setup_route_log(PyObject* self, PyObject* args) {
    PyObject* func;
    PyObject* warn;

    if (!PyArg_ParseTuple(
        args,
        "OO",
        &func,
        &warn
        ))
        return NULL;

    if (!PyCallable_Check(func)) {
        PyErr_Format(
            PyExc_RuntimeError,
            "setup_route_log got non-function object: %R",
            func
        );
        return NULL;
    }

    if (!PyCallable_Check(warn)) {
        PyErr_Format(
            PyExc_RuntimeError,
            "setup_route_log got non-function object: %R",
            warn
        );
        return NULL;
    }

    route_log = Py_NewRef(func);
    route_warn = Py_NewRef(warn);

    Py_RETURN_NONE;
}

static PyObject* register_ws_cls(PyObject* self, PyObject* args) {
    PyObject* cls;
    PyObject* ws_disconnect_err_val;
    PyObject* ws_err_cls_val;

    if (!PyArg_ParseTuple(args, "OOO", &cls, &ws_disconnect_err_val, &
        ws_err_cls_val))
        return NULL;

    if (!PyType_Check(cls)) {
        PyErr_Format(PyExc_RuntimeError,
            "register_ws_cls got non-type object: %R", cls);
        return NULL;
    }

    if (!PyType_Check(ws_disconnect_err_val)) {
        PyErr_Format(PyExc_RuntimeError,
            "register_ws_cls got non-type object: %R", cls);
        return NULL;
    }

    if (!PyType_Check(ws_err_cls_val)) {
        PyErr_Format(PyExc_RuntimeError,
            "register_ws_cls got non-type object: %R", cls);
        return NULL;
    }

    ws_cls = Py_NewRef(cls);
    ws_disconnect_err = Py_NewRef(ws_disconnect_err_val);
    ws_err_cls = Py_NewRef(ws_err_cls_val);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"setup_route_log", setup_route_log, METH_VARARGS, NULL},
    {"register_ws_cls", register_ws_cls, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_view",
    NULL,
    -1,
    methods,
    #if PY_MINOR_VERSION >= 12
    {
        {Py_mod_multiple_interpreters,
         Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
        {0, NULL}
    }
    #endif
};

NORETURN void view_fatal(
    const char* message,
    const char* where,
    const char* func,
    int lineno
) {
    fprintf(
        stderr,
        "_view FATAL ERROR at [%s:%d] in %s: %s\n",
        where,
        lineno,
        func,
        message
    );
    fputs(
        "Please report this at https://github.com/ZeroIntensity/view.py/issues\n",
        stderr
    );
    Py_FatalError("view.py core died");
};

PyMODINIT_FUNC PyInit__view() {
    PyObject* m = PyModule_Create(&module);

    if ((PyType_Ready(&PyAwaitable_Type) < 0) ||
        (PyType_Ready(&ViewAppType) < 0) ||
        (PyType_Ready(&_PyAwaitable_GenWrapper_Type) < 0) ||
        (PyType_Ready(&ContextType) < 0) ||
        (PyType_Ready(&TCPublicType) < 0) ||
        (PyType_Ready(&WebSocketType) < 0) ||
        (PyType_Ready(&HeaderDictType) < 0)) {
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
    if (PyModule_AddObject(
        m,
        "Context",
        (PyObject*) &ContextType
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&TCPublicType);
    if (PyModule_AddObject(
        m,
        "TCPublic",
        (PyObject*) &TCPublicType
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&WebSocketType);
    if (PyModule_AddObject(
        m,
        "ViewWebSocket",
        (PyObject*) &WebSocketType
        ) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&HeaderDictType);
    if (PyModule_AddObject(m, "HeaderDict", (PyObject*) &HeaderDictType) < 0) {
        Py_DECREF(m);
        return NULL;
    }


    PyObject* ipaddress_mod = PyImport_ImportModule("ipaddress");
    if (!ipaddress_mod) {
        Py_DECREF(m);
        return NULL;
    }

    ip_address = PyObject_GetAttrString(
        ipaddress_mod,
        "ip_address"
    );
    if (!ip_address) {
        Py_DECREF(m);
        Py_DECREF(ipaddress_mod);
        return NULL;
    }
    Py_DECREF(ipaddress_mod);

    invalid_status_error = PyErr_NewException(
        "_view.InvalidStatusError",
        PyExc_RuntimeError,
        NULL
    );
    if (!invalid_status_error) {
        Py_DECREF(m);
        Py_DECREF(ip_address);
        return NULL;
    }

    if (PyModule_AddObject(
        m,
        "InvalidStatusError",
        invalid_status_error
        ) < 0) {
        Py_DECREF(m);
        Py_DECREF(ip_address);
        Py_DECREF(invalid_status_error);
        return NULL;
    }

    return m;
}
