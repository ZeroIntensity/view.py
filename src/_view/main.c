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
#include <view/context.h> // ContextType
#include <view/headerdict.h> // HeaderDictType
#include <view/results.h> // build_default_headers
#include <view/ws.h> // WebSocketType
#include <view/view.h>

#define PYAWAITABLE_THIS_FILE_INIT
#include <pyawaitable.h>

PyObject *route_log = NULL;
PyObject *route_warn = NULL;
PyObject *ip_address = NULL;
PyObject *invalid_status_error = NULL;
PyObject *default_headers = NULL;

/*
 * Register route logging functions.
 *
 * As of now, this stores only the route logger, and the
 * service warning function.
 */
static PyObject *
setup_route_log(PyObject *self, PyObject *args)
{
    PyObject *func;
    PyObject *warn;

    if (
        !PyArg_ParseTuple(
            args,
            "OO",
            &func,
            &warn
        )
    )
        return NULL;

    if (!PyCallable_Check(func))
    {
        PyErr_Format(
            PyExc_RuntimeError,
            "setup_route_log got non-function object: %R",
            func
        );
        return NULL;
    }

    if (!PyCallable_Check(warn))
    {
        PyErr_Format(
            PyExc_RuntimeError,
            "setup_route_log got non-function object: %R",
            warn
        );
        return NULL;
    }

    route_log = Py_NewRef(func);
    route_warn = Py_NewRef(warn);

    if (PyModule_AddObject(self, "route_log", route_log) < 0)
    {
        Py_DECREF(route_log);
        Py_DECREF(route_warn);
        return NULL;
    }

    if (PyModule_AddObject(self, "route_warn", route_warn) < 0)
    {
        Py_DECREF(route_warn);
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject *
dummy_context(PyObject *self, PyObject *app)
{
    return context_from_data(app, NULL);
}

static PyObject *
test_awaitable(PyObject *self, PyObject *args)
{
    PyObject *func;
    if (!PyArg_ParseTuple(args, "O", &func))
        return NULL;

    PyObject *res = PyObject_CallNoArgs(func);
    if (!res)
        return NULL;

    PyObject *awaitable = PyAwaitable_New();
    if (!awaitable)
    {
        Py_DECREF(res);
        return NULL;
    }

    if (PyAwaitable_AddAwait(awaitable, res, NULL, NULL) < 0)
    {
        Py_DECREF(awaitable);
        Py_DECREF(res);
        return NULL;
    }

    return awaitable;
}

static PyMethodDef methods[] =
{
    {"test_awaitable", test_awaitable, METH_VARARGS, NULL},
    {"setup_route_log", setup_route_log, METH_VARARGS, NULL},
    {"dummy_context", dummy_context, METH_O, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module =
{
    PyModuleDef_HEAD_INIT,
    "_view",
    NULL,
    -1,
    methods,
};

/*
 * Crash Python and view.py with a fatal error.
 *
 * Don't use this directly! Use the VIEW_FATAL macro instead.
 */
NORETURN void
view_fatal(
    const char *message,
    const char *where,
    const char *func,
    int lineno
)
{
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

int
exec_module(PyObject *mod)
{
    if (PyModule_AddType(mod, &ViewAppType) < 0)
    {
        return -1;
    }

    if (PyModule_AddType(mod, &ContextType) < 0)
    {
        return -1;
    }

    if (PyModule_AddType(mod, &TCPublicType) < 0)
    {
        return -1;
    }

    if (PyModule_AddType(mod, &WebSocketType) < 0)
    {
        return -1;
    }

    if (PyModule_AddType(mod, &HeaderDictType) < 0)
    {
        return -1;
    }

    if (
        PyModule_Add(
            mod,
            "InvalidStatusError",
            PyErr_NewException(
                "_view.InvalidStatusError",
                PyExc_RuntimeError,
                NULL
            )
        ) < 0
    )
    {
        return -1;
    }

    default_headers = build_default_headers();
    if (default_headers == NULL)
    {
        return -1;
    }

    if (PyModule_AddObject(mod, "default_headers", default_headers) < 0)
    {
        Py_DECREF(default_headers);
        return -1;
    }

    if (PyAwaitable_Init() < 0)
    {
        return -1;
    }

    return 0;
}

static struct PyModuleDef_Slot slots[] =
{
    {Py_mod_exec, exec_module},
#if PY_MINOR_VERSION >= 12
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#endif
#if PY_MINOR_VERSION >= 13
    {Py_mod_gil, Py_MOD_GIL_USED},
#endif
    {0, NULL},
};

PyModuleDef module_def =
{
    PyModuleDef_HEAD_INIT,
    .m_name = "_view",
    .m_size = 0, // TODO: Support subinterpreters
    .m_methods = methods,
    .m_slots = slots
};

PyMODINIT_FUNC
PyInit__view(void)
{
    return PyModuleDef_Init(&module_def);
}
