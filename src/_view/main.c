#include <Python.h>
#include <view/view.h>
#include <threads.h>

#define METHOD(name)                                                           \
  {                                                                            \
#name, name, METH_VARARGS, NULL                                            \
  }
#define METHOD_NOARGS(name)                                                    \
  {                                                                            \
#name, name, METH_NOARGS, NULL                                             \
  }

static void* io(PyObject* awaitable) {
    puts("running");
    PyInterpreterState_Get();
    thrd_sleep(
        &(struct timespec){.tv_sec = 1},
        NULL
    );
    return "123";
}

static int callback(PyObject* awaitable, void* result) {
    printf(
        "result: %s\n",
        (char*) result
    );
    return 0;
}

PyObject* test(PyObject* self, PyObject* args) {
    PyObject* awaitable = PyAwaitable_New();

    if (PyAwaitable_VirtualAwait(
        awaitable,
        io,
        callback
        ) < 0) {
        return NULL;
    }

    return awaitable;
}

static PyMethodDef methods[] = {METHOD(test), {NULL, NULL, 0, NULL}};

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
        (PyObject*)&PyAwaitable_Type
        ) < 0) {
        Py_DECREF(&PyAwaitable_Type);
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&ViewAppType);

    if (PyModule_AddObject(
        m,
        "ViewApp",
        (PyObject*)&ViewAppType
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
        (PyObject*)&_PyAwaitable_GenWrapper_Type
        ) < 0) {
        Py_DECREF(&ViewAppType);
        Py_DECREF(&PyAwaitable_Type);
        Py_DECREF(&_PyAwaitable_GenWrapper_Type);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
