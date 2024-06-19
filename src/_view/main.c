/*
 * The _view extension module definition
 *
 * This is where all attributes of the extension module are initialized.
 * Type stubs for the module are defined in the _view.pyi file.
 *
 * Most things the view.py C API are private APIs - they can make
 * breaking changes without a deprecation period.
 *
 * Python objects stored at global scope are initialized by the module
 * initialization function (PyInit__view). Generally, Python objects at
 * global scope are one of two things:
 *
 * - A Python object that needs to be used from C, such as an exception class.
 * - A Python API that needs to be called from the C API, such as `ipaddress.ip_address`.
 *
 * Some APIs are at global scope, but stored on the module to allow Python to manage
 * it's reference count, such as the default headers. If they were only stored
 * at global scope, then there would be no way for view.py to know when to decrement
 * their reference count and deallocate it, causing a memory leak when the module
 * is deallocated.
 */
#include <Python.h>
#include <signal.h>

#include <view/app.h> // ViewAppType
#include <view/awaitable.h> // PyAwaitable_Type, _PyAwaitable_GenWrapper_Type
#include <view/context.h> // ContextType
#include <view/headerdict.h> // HeaderDictType
#include <view/results.h> // build_default_headers
#include <view/ws.h> // WebSocketType
#include <view/view.h>

// Module object instance, this is not exported!
PyObject* m = NULL;

PyObject* route_log = NULL;
PyObject* route_warn = NULL;
PyObject* ip_address = NULL;
PyObject* invalid_status_error = NULL;
PyObject* ws_cls = NULL;
PyObject* ws_disconnect_err = NULL;
PyObject* ws_err_cls = NULL;
PyObject* default_headers = NULL;

/*
 * Register route logging functions.
 *
 * As of now, this stores only the route logger, and the
 * service warning function.
 */
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

    if (PyModule_AddObject(m, "route_log", route_log) < 0) {
        Py_DECREF(route_log);
        Py_DECREF(route_warn);
        return NULL;
    }

    if (PyModule_AddObject(m, "route_warn", route_warn) < 0) {
        Py_DECREF(route_warn);
        return NULL;
    }

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
    // TODO: add PyModule_AddObject here

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

/*
 * Crash Python and view.py with a fatal error.
 *
 * Don't use this directly! Use the VIEW_FATAL macro instead.
 */
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
    m = PyModule_Create(&module);

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

    // We want python to manage this memory, so we have to put it on the module.
    // This won't be on the type stub, though.
    if (PyModule_AddObject(m, "ip_address", ip_address) < 0) {
        Py_DECREF(m);
        Py_DECREF(ip_address);
        return NULL;
    }

    invalid_status_error = PyErr_NewException(
        "_view.InvalidStatusError",
        PyExc_RuntimeError,
        NULL
    );
    if (!invalid_status_error) {
        Py_DECREF(m);
        return NULL;
    }

    if (PyModule_AddObject(
        m,
        "InvalidStatusError",
        invalid_status_error
        ) < 0) {
        Py_DECREF(m);
        Py_DECREF(invalid_status_error);
        return NULL;
    }

    default_headers = build_default_headers();
    if (!default_headers) {
        Py_DECREF(m);
        return NULL;
    }

    // Once again, reference management should be delegated to Python.
    // Will not be on the type stub either.
    if (PyModule_AddObject(m, "default_headers", default_headers) < 0) {
        Py_DECREF(m);
        Py_DECREF(default_headers);
        return NULL;
    }

    return m;
}
