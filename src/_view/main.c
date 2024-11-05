/*
 * The _view extension module definition
 *
 * This is where all attributes of the extension module are initialized.
 * Type stubs for the module are defined in the _view.pyi file.
 *
 * Most things the view.py C API are private APIs - they can make
 * breaking changes without a deprecation period.
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

PyObject *
dummy_context(PyObject *self, PyObject *app)
{
    return context_from_data(app, NULL);
}

static PyMethodDef methods[] =
{
    {"dummy_context", dummy_context, METH_O, NULL},
    {NULL, NULL, 0, NULL}
};

static int
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
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
#endif
#if PY_MINOR_VERSION >= 13
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL},
};

static PyModuleDef module_def =
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
