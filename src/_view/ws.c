#include <view/view.h>
#include <Python.h>
#include <stddef.h> // offsetof

typedef struct {
    PyObject_HEAD
    PyObject* send;
    PyObject* receive;
} WebSocket;

static PyObject* repr(PyObject* self) {
    WebSocket* ws = (WebSocket*) self;
    return PyUnicode_FromFormat("_WebSocket(%p)", self);
}

static void dealloc(WebSocket* self) {
    Py_XDECREF(self->send);
    Py_XDECREF(self->receive);
    Py_TYPE(self)->tp_free((PyObject*) self);
}

static PyObject* WebSocket_new(
    PyTypeObject* type,
    PyObject* args,
    PyObject* kwargs
) {
    WebSocket* self = (WebSocket*) type->tp_alloc(
        type,
        0
    );
    if (!self)
        return NULL;

    return (PyObject*) self;
}

PyObject* ws_from_data(PyObject* send, PyObject* receive) {
    WebSocket* ws = (WebSocket*) WebSocket_new(
        &WebSocketType,
        NULL,
        NULL
    );

    ws->send = Py_NewRef(send);
    ws->receive = Py_NewRef(receive);
    return (PyObject*) ws;
}

static int run_ws_accept(PyObject* awaitable, PyObject* result) {
    PyObject* tp = PyDict_GetItemString(
        result,
        "type"
    );
    if (!tp)
        return -1;

    const char* type = PyUnicode_AsUTF8(tp);
    if (!type)
        return -1;

    if (!strcmp(
        type,
        "websocket.disconnect"
        )) {

        return 0;
    }

    if (strcmp(
        type,
        "websocket.connect"
        )) {
        // type is probably websocket.receive, so accept() was already called
        PyErr_SetString(
            ws_handshake_error,
            "received message was not websocket.connect (was accept() already called?)"
        );
        return -1;
    }

    WebSocket* ws;
    if (PyAwaitable_UnpackValues(
        awaitable,
        &ws
        ) < 0)
        return -1;

    PyObject* send_dict = Py_BuildValue(
        "{s:s}",
        "type",
        "websocket.accept"
    );
    if (!send_dict)
        return -1;

    PyObject* coro = PyObject_Vectorcall(
        ws->send,
        (PyObject*[]) { send_dict },
        1,
        NULL
    );
    Py_DECREF(send_dict);

    if (!coro)
        return -1;

    if (PyAwaitable_AWAIT(
        awaitable,
        coro
        ) < 0) {
        Py_DECREF(coro);
        return -1;
    }

    return 0;
}

static int run_ws_recv(PyObject* awaitable, PyObject* result) {
    PyObject* tp = PyDict_GetItemString(
        result,
        "type"
    );
    if (!tp)
        return -1;

    const char* type = PyUnicode_AsUTF8(tp);
    if (!type)
        return -1;

    if (!strcmp(
        type,
        "websocket.disconnect"
        )) {
        return 0;
    }

    if (strcmp(
        type,
        "websocket.receive"
        )) {
        // type is probably websocket.connect, so accept() was not called
        PyErr_SetString(
            ws_handshake_error,
            "received message was not websocket.receive (did you forget to call accept()?)"
        );
        return -1;
    }

    PyObject* text = PyDict_GetItemString(
        result,
        "text"
    );

    if (!text || (text == Py_None)) {
        text = PyDict_GetItemString(
            result,
            "bytes"
        );

        if (!text || (text == Py_None)) {
            PyErr_BadASGI();
            return -1;
        }
    };

    if (PyAwaitable_SetResult(
        awaitable,
        Py_NewRef(text)
        ) < 0) {
        Py_DECREF(text);
        return -1;
    }

    return 0;
}

static int ws_err(
    PyObject* awaitable,
    PyObject* tp,
    PyObject* value,
    PyObject* tb
) {
    // NOTE: this needs to be here for the error to propagate! otherwise, the error is deferred to the ASGI server (which we don't want)
    PyErr_Restore(tp, value, tb);
    PyErr_Print();
    PyErr_Clear();
    PyAwaitable_Cancel(awaitable);
    return -2;
}

static PyObject* recv_awaitable(WebSocket* self, awaitcallback cb) {
    PyObject* recv_coro = PyObject_CallNoArgs(self->receive);
    if (!recv_coro)
        return NULL;

    PyObject* awaitable = PyAwaitable_New();
    if (!awaitable) {
        Py_DECREF(recv_coro);
        return NULL;
    }

    if (PyAwaitable_SaveValues(
        awaitable,
        1,
        self
        ) < 0) {
        Py_DECREF(awaitable);
        Py_DECREF(recv_coro);
        return NULL;
    }

    if (PyAwaitable_AddAwait(
        awaitable,
        recv_coro,
        cb,
        ws_err
        ) < 0) {
        Py_DECREF(recv_coro);
        return NULL;
    };

    Py_DECREF(recv_coro);
    return awaitable;
}

static PyObject* WebSocket_accept(WebSocket* self) {
    return recv_awaitable(
        self,
        run_ws_accept
    );
}

static PyObject* WebSocket_receive(WebSocket* self) {
    return recv_awaitable(
        self,
        run_ws_recv
    );
}

static PyObject* WebSocket_close(
    WebSocket* self,
    PyObject* args,
    PyObject* kwargs
) {
    static char* kwlist[] = {"code", "reason", NULL};
    PyObject* code = NULL;
    PyObject* reason = NULL;

    if (!PyArg_ParseTupleAndKeywords(
        args,
        kwargs,
        "|O!O!",
        kwlist,
        &PyLong_Type,
        &code,
        &PyUnicode_Type,
        &reason
        ))
        return NULL;

    PyObject* awaitable = PyAwaitable_New();
    if (!awaitable)
        return NULL;

    PyObject* send_dict = Py_BuildValue(
        "{s:s}",
        "type",
        "websocket.close"
    );
    if (!send_dict) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (code) {
        if (PyDict_SetItemString(
            send_dict,
            "code",
            code
            ) < 0) {
            Py_DECREF(awaitable);
            Py_DECREF(send_dict);
            return NULL;
        }
    }

    if (reason) {
        if (PyDict_SetItemString(
            send_dict,
            "reason",
            reason
            ) < 0) {
            Py_DECREF(awaitable);
            Py_DECREF(send_dict);
            return NULL;
        }
    }

    PyObject* coro = PyObject_Vectorcall(
        self->send,
        (PyObject*[]) { send_dict },
        1,
        NULL
    );
    Py_DECREF(send_dict);

    if (!coro) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyAwaitable_AWAIT(
        awaitable,
        coro
        ) < 0) {
        Py_DECREF(awaitable);
        return NULL;
    }

    Py_DECREF(coro);
    return awaitable;
}


static PyObject* WebSocket_send(WebSocket* self, PyObject* args) {
    PyObject* data;

    if (!PyArg_ParseTuple(
        args,
        "O",
        &data
        ))
        return NULL;

    PyObject* awaitable = PyAwaitable_New();
    if (!awaitable)
        return NULL;

    PyObject* send_dict = Py_BuildValue(
        "{s:s,s:S}",
        "type",
        "websocket.send",
        "text",
        data
    );

    if (!send_dict) {
        Py_DECREF(awaitable);
        return NULL;
    }

    PyObject* coro = PyObject_Vectorcall(
        self->send,
        (PyObject*[]) { send_dict },
        1,
        NULL
    );
    Py_DECREF(send_dict);

    if (!coro) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyAwaitable_AWAIT(
        awaitable,
        coro
        ) < 0) {
        Py_DECREF(awaitable);
        Py_DECREF(coro);
        return NULL;
    }

    Py_DECREF(coro);
    return awaitable;
}

static PyMethodDef methods[] = {
    {"accept", (PyCFunction) WebSocket_accept, METH_NOARGS, NULL},
    {"receive", (PyCFunction) WebSocket_receive, METH_NOARGS, NULL},
    {"close", (PyCFunction) WebSocket_close, METH_VARARGS | METH_KEYWORDS,
     NULL},
    {"send", (PyCFunction) WebSocket_send, METH_VARARGS, NULL},
    {NULL}
};

PyTypeObject WebSocketType = {
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.ViewWebSocket",
    .tp_basicsize = sizeof(WebSocket),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = WebSocket_new,
    .tp_dealloc = (destructor) dealloc,
    .tp_repr = repr,
    .tp_methods = methods
};
