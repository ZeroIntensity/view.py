#include <Python.h>
#include <view/app.h>
#include <view/awaitable.h>
#include <stdbool.h>

typedef struct {
    PyObject_HEAD;
    PyObject* startup;
    PyObject* cleanup;
} ViewApp;

static PyObject* new(PyTypeObject* tp, PyObject* args, PyObject* kwds) {
    ViewApp* self = (ViewApp*) tp->tp_alloc(
        tp,
        0
    );
    if (!self) return NULL;
    self->startup = NULL;
    self->cleanup = NULL;

    return (PyObject*) self;
}

static int init(PyObject* self, PyObject* args, PyObject* kwds) {
    PyErr_SetString(
        PyExc_TypeError,
        "ViewApp is not constructable"
    );
    return -1;
}
static int lifespan(PyObject* awaitable, PyObject* result) {
    ViewApp* self;
    PyObject* send;
    PyObject* receive;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        NULL,
        &receive,
        &send
        ) < 0)
        return -1;

    Py_INCREF(self);
    Py_INCREF(receive);
    Py_INCREF(send);
    if (!send) return -1;

    PyObject* tp = PyDict_GetItemString(
        result,
        "type"
    );
    const char* type = PyUnicode_AsUTF8(tp);
    Py_DECREF(tp);

    bool is_startup = !strcmp(
        type,
        "lifespan.startup"
    );
    PyObject* target_obj = is_startup ? self->startup : self->cleanup;

    if (target_obj) {
        if (!PyObject_CallNoArgs(target_obj)) {
            Py_DECREF(awaitable);
            Py_DECREF(receive);
            Py_DECREF(send);
            return -1;
        }
    }

    PyObject* send_coro = PyObject_CallFunction(
        send,
        "{s:s}",
        "type",
        is_startup ? "lifespan.startup.complete" : "lifespan.shutdown.complete"
    );

    if (!send_coro) {
        Py_DECREF(awaitable);
        Py_DECREF(send);
        Py_DECREF(receive);
        return -1;
    }

    if (PyAwaitable_AddAwait(
        awaitable,
        send_coro,
        NULL
        ) < 0) {
        Py_DECREF(awaitable);
        Py_DECREF(send);
        Py_DECREF(receive);
        Py_DECREF(send_coro);
        return -1;
    }
    Py_DECREF(send_coro);
    Py_DECREF(send);

    if (!is_startup) return 0;

    PyObject* recv_coro = PyObject_CallNoArgs(receive);
    if (!recv_coro) {
        Py_DECREF(receive);
        Py_DECREF(awaitable);
        return -1;
    }

    if (PyAwaitable_AddAwait(
        awaitable,
        recv_coro,
        lifespan
        ) < 0) {
        Py_DECREF(awaitable);
        Py_DECREF(receive);
        Py_DECREF(recv_coro);
        return -1;
    };

    return 0;
}

static void dealloc(ViewApp* self) {
    Py_XDECREF(self->cleanup);
    Py_XDECREF(self->startup);
    Py_TYPE(self)->tp_free(self);
}

static PyObject* app(ViewApp* self, PyObject* args) {
    PyObject* scope;
    PyObject* receive;
    PyObject* send;
    if (!PyArg_ParseTuple(
        args,
        "OOO",
        &scope,
        &receive,
        &send
        )) return NULL;

    PyObject* tp = PyDict_GetItemString(
        scope,
        "type"
    );
    if (!tp)
        return NULL;

    const char* type = PyUnicode_AsUTF8(tp);
    Py_DECREF(tp);

    PyObject* awaitable = PyAwaitable_New();

    if (!awaitable)
        return NULL;

    if (PyAwaitable_SaveValues(
        awaitable,
        4,
        Py_NewRef(self),
        Py_NewRef(scope),
        Py_NewRef(receive),
        Py_NewRef(send)
        ) < 0) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (!strcmp(
        type,
        "lifespan"
        )) {
        PyObject* recv_coro = PyObject_CallNoArgs(receive);
        if (!recv_coro) {
            Py_DECREF(awaitable);
            return NULL;
        }

        if (PyAwaitable_AddAwait(
            awaitable,
            recv_coro,
            lifespan
            ) < 0) {
            Py_DECREF(awaitable);
            Py_DECREF(recv_coro);
            return NULL;
        };
        return awaitable;
    }

    PyObject* coro = PyObject_CallFunction(
        send,
        "{s:s,s:i,s:[[yy]]}",
        "type",
        "http.response.start",
        "status",
        200,
        "headers",
        "content-type",
        "text/plain"
    );

    if (!coro) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyAwaitable_AddAwait(
        awaitable,
        coro,
        NULL
        ) < 0) {
        Py_DECREF(awaitable);
        Py_DECREF(coro);
        return NULL;
    };

    Py_DECREF(coro);

    coro = PyObject_CallFunction(
        send,
        "{s:s,s:y}",
        "type",
        "http.response.body",
        "body",
        "Hello, World!"
    );

    if (!coro) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyAwaitable_AddAwait(
        awaitable,
        coro,
        NULL
        ) < 0) {
        Py_DECREF(awaitable);
        Py_DECREF(coro);
        return NULL;
    }

    Py_DECREF(coro);

    return awaitable;
}

static PyMethodDef methods[] = {
    {"asgi_app_entry", (PyCFunction) app, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

PyTypeObject ViewAppType = {
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.ViewApp",
    .tp_basicsize = sizeof(ViewApp),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_init = (initproc) init,
    .tp_methods = methods,
    .tp_new = new,
    .tp_dealloc = (destructor) dealloc
};
