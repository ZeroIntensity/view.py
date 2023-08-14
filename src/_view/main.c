#include <Python.h>
#include <view/view.h>
#include <threads.h>

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

PyMODINIT_FUNC PyInit__view() {
    PyObject* m = PyModule_Create(&module);

    if ((PyType_Ready(&PyAwaitable_Type) < 0) ||
        (PyType_Ready(&ViewAppType) < 0) ||
        (PyType_Ready(&_PyAwaitable_GenWrapper_Type) < 0)) {
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
    /*
       Py_INCREF(&ContextType);
       if (PyModule_AddObject(
        m,
        "Context",
        (PyObject*) &ContextType
        ) < 0) {
        Py_DECREF(&ContextType);
        Py_DECREF(&ViewAppType);
        Py_DECREF(&PyAwaitable_Type);
        Py_DECREF(&_PyAwaitable_GenWrapper_Type);
        Py_DECREF(m);
        return NULL;
       }
     */
    return m;
}
