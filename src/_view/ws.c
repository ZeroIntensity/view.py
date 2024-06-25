/*
 * view.py ASGI WebSocket implementation
 *
 * This file contains the internal _WebSocket object, as well
 * as all the logic for dealing with WebSockets.
 *
 * While the WebSocket API is public, it is wrapped by a Python class,
 * hence why the object name here is _WebSocket, meaning that
 * breaking API changes can be made here.
 *
 * The _WebSocket class is fairly simple, if you're familiar with ASGI. The
 * object wraps both the ASGI send() and receive() function, which are passed through
 * the data input constructor: ws_from_data()
 *
 * In fact, similar to Context, that's really the only way to construct a WebSocket
 * object at runtime, as the WebSocket __new__() doesn't do any argument parsing. All
 * fields of WebSocket are set by ws_from_data()
 *
 * The underlying WebSocket methods are just simple PyAwaitable calls:
 *
 * - accept() is implemented by calling send() with a "websocket.accept"
 * - receive() is implemented by calling the ASGI receive()
 * - close() is implemented by sending a "websocket.close". Note that this
 *   function sets the closing field to true, which prevents any further
 *   calls. closing can be set without the underlying connection actually
 *   being finalized yet.
 */
#include <Python.h>
#include <stddef.h> // offsetof

#include <view/app.h> // PyErr_BadASGI
#include <view/pyawaitable.h>
#include <view/backport.h>
#include <view/results.h> // handle_result
#include <view/route.h> // route
#include <view/ws.h> // WebSocketType
#include <view/view.h>

typedef struct
{
    PyObject_HEAD
    PyObject *send; // ASGI send()
    PyObject *receive; // ASGI receive()
    PyObject *raw_path; // Path from the ASGI scope
    bool closing; // This is set upon calling close(), regardless of whether the connection has actually finalized
} WebSocket;

/* Deallocator for the WebSocket object. */
static void
dealloc(WebSocket *self)
{
    Py_XDECREF(self->send);
    Py_XDECREF(self->receive);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

/*
 * WebSocket object allocator.
 *
 * Note that this does not set any fields, it only allocates the
 * object. Generally, you don't want to call this manually. Use
 * the ws_from_data() function instead.
 */
static PyObject *
WebSocket_new(
    PyTypeObject *type,
    PyObject *args,
    PyObject *kwargs
)
{
    WebSocket *self = (WebSocket *) type->tp_alloc(
        type,
        0
    );
    if (!self)
        return NULL;

    return (PyObject *) self;
}

/*
 * The main WebSocket initializer.
 *
 * Note that this does not actually return a _WebSocket() instance, but
 * instead an instance of the Python WebSocket() class.
 */
PyObject *
ws_from_data(PyObject *scope, PyObject *send, PyObject *receive)
{
    WebSocket *ws = (WebSocket *) WebSocket_new(
        &WebSocketType,
        NULL,
        NULL
    );

    if (!ws)
        return NULL;

    ws->send = Py_NewRef(send);
    ws->receive = Py_NewRef(receive);
    ws->raw_path = Py_XNewRef(PyDict_GetItemString(scope, "path"));

    if (!ws->raw_path)
    {
        PyErr_BadASGI();
        return NULL;
    }

    PyObject *py_ws = PyObject_Vectorcall(
        ws_cls,
        (PyObject *[]) { (PyObject *) ws },
        1,
        NULL
    );

    return py_ws;
}

/*
 * Actual implementation of accept(). Do not call this manually!
 *
 * This is a PyAwaitable callback set by recv_awaitable(), it is
 * given the result of the call to the ASGI receive() function.
 *
 * This expects that the "type" key in the result is "websocket.receive." If not,
 * a RuntimeError is thrown.
 *
 * If the WebSocket disconnected between calls (i.e. the "type" key is "websocket.disconnect"),
 * then this returns None back to the user through PyAwaitable.
 *
 * It is up to the Python caller to handle the result of this function.
 */
static int
run_ws_accept(PyObject *awaitable, PyObject *result)
{
    PyObject *tp = PyDict_GetItemString(
        result,
        "type"
    );
    if (!tp)
    {
        PyErr_BadASGI();
        return -1;
    }

    const char *type = PyUnicode_AsUTF8(tp);
    if (!type)
        return -1;

    if (
        !strcmp(
            type,
            "websocket.disconnect"
        )
    )
    {
        return 0;
    }

    if (
        strcmp(
            type,
            "websocket.connect"
        )
    )
    {
        // type is probably websocket.receive, so accept() was already called
        PyErr_SetString(
            PyExc_RuntimeError,
            "received message was not websocket.connect (was accept() already called?)"
        );
        return -1;
    }

    WebSocket *ws;
    if (
        PyAwaitable_UnpackValues(
            awaitable,
            &ws
        ) < 0
    )
        return -1;

    PyObject *send_dict = Py_BuildValue(
        "{s:s}",
        "type",
        "websocket.accept"
    );
    if (!send_dict)
        return -1;

    PyObject *coro = PyObject_Vectorcall(
        ws->send,
        (PyObject *[]) { send_dict },
        1,
        NULL
    );
    Py_DECREF(send_dict);

    if (!coro)
        return -1;

    if (
        PyAwaitable_AWAIT(
            awaitable,
            coro
        ) < 0
    )
    {
        Py_DECREF(coro);
        return -1;
    }
    PyObject *args = Py_BuildValue(
        "(zOz)",
        "N/A",
        ws->raw_path,
        "websocket"
    );

    if (!PyObject_Call(route_log, args, NULL))
    {
        Py_DECREF(args);
        Py_DECREF(awaitable);
        return -1;
    }
    Py_DECREF(args);

    return 0;
}

/*
 * Actual implementation of receive(). Do not call this manually!
 *
 * This behaves nearly exactly the same as accept(), with the
 * exception of the return value.
 */
static int
run_ws_recv(PyObject *awaitable, PyObject *result)
{
    PyObject *tp = PyDict_GetItemString(
        result,
        "type"
    );
    if (!tp)
        return -1;

    const char *type = PyUnicode_AsUTF8(tp);
    if (!type)
        return -1;

    if (
        !strcmp(
            type,
            "websocket.disconnect"
        )
    )
    {
        return 0;
    }

    if (
        strcmp(
            type,
            "websocket.receive"
        )
    )
    {
        // type is probably websocket.connect, so accept() was not called
        PyErr_SetString(
            PyExc_RuntimeError,
            "received message was not websocket.receive (did you forget to call accept()?)"
        );
        return -1;
    }

    PyObject *text = PyDict_GetItemString(
        result,
        "text"
    );

    if (!text || (text == Py_None))
    {
        text = PyDict_GetItemString(
            result,
            "bytes"
        );

        if (!text || (text == Py_None))
        {
            PyErr_BadASGI();
            return -1;
        }
    }
    ;

    if (
        PyAwaitable_SetResult(
            awaitable,
            Py_NewRef(text)
        ) < 0
    )
    {
        Py_DECREF(text);
        return -1;
    }

    return 0;
}

/*
 * Simple wrapper around exceptions that occur during
 * asynchronous calls in WebSocket connections.
 */
static int
ws_err(
    PyObject *awaitable,
    PyObject *err
)
{
    /*
     * This needs to be here for the error to propagate at runtime.
     *
     * All this does is print the error and clear the error indicator, to
     * prevent the ASGI server from handling it weirdly.
     */
    PyErr_SetRaisedException(err);
    PyErr_Print();
    PyErr_Clear();
    PyAwaitable_Cancel(awaitable);
    return -2;
}

/*
 * Utility function for calling receive() with a PyAwaitable callback.
 *
 * Most of the _WebSocket() methods call this function, and keep
 * their logic in a method-specific callback. For example, accept() is
 * implemented by calling this function with run_ws_accept() as the callback.
 */
static PyObject *
recv_awaitable(WebSocket *self, awaitcallback cb)
{
    PyObject *recv_coro = PyObject_CallNoArgs(self->receive);
    if (!recv_coro)
        return NULL;

    PyObject *awaitable = PyAwaitable_New();
    if (!awaitable)
    {
        Py_DECREF(recv_coro);
        return NULL;
    }

    if (
        PyAwaitable_SaveValues(
            awaitable,
            1,
            self
        ) < 0
    )
    {
        Py_DECREF(awaitable);
        Py_DECREF(recv_coro);
        return NULL;
    }

    if (
        PyAwaitable_AddAwait(
            awaitable,
            recv_coro,
            cb,
            ws_err
        ) < 0
    )
    {
        Py_DECREF(recv_coro);
        return NULL;
    }
    ;

    Py_DECREF(recv_coro);
    return awaitable;
}

/*
 * Actual Python method for accept()
 *
 * This defers to PyAwaitable, which calls run_ws_accept(), which
 * is the actual implementation function.
 */
static PyObject *
WebSocket_accept(WebSocket *self)
{
    if (self->closing)
    {
        PyErr_SetString(PyExc_RuntimeError, "websocket has been closed");
        return NULL;
    }
    return recv_awaitable(
        self,
        run_ws_accept
    );
}

/*
 * Actual Python method for receive()
 *
 * This is an asynchronous function.
 */
static PyObject *
WebSocket_receive(WebSocket *self)
{
    /*
     * This defers to PyAwaitable, which calls run_ws_recv(), which
     * is the actual implementation function.
     */
    if (self->closing)
    {
        PyErr_SetString(PyExc_RuntimeError, "websocket has been closed");
        return NULL;
    }
    return recv_awaitable(
        self,
        run_ws_recv
    );
}

/*
 * Python method for closing the connection.
 *
 * This takes two keyword arguments at the Python level: code and reason.
 * Code is the WebSocket close code, and reason is a string containing the reason why.
 *
 * Validating these are up to the Python caller, not C.
 */
static PyObject *
WebSocket_close(
    WebSocket *self,
    PyObject *args,
    PyObject *kwargs
)
{
    /*
     * This still counts as a private API - the WebSocket() class that
     * wraps it is what's public.
     */
    static char *kwlist[] = {"code", "reason", NULL};
    PyObject *code = NULL;
    PyObject *reason = NULL;

    if (
        !PyArg_ParseTupleAndKeywords(
            args,
            kwargs,
            "|O!O!",
            kwlist,
            &PyLong_Type,
            &code,
            &PyUnicode_Type,
            &reason
        )
    )
        return NULL;

    if (self->closing)
    {
        PyErr_SetString(
            PyExc_RuntimeError,
            "websocket is already closed or closing"
        );
        return NULL;
    }

    PyObject *awaitable = PyAwaitable_New();
    if (!awaitable)
        return NULL;

    PyObject *send_dict = Py_BuildValue(
        "{s:s}",
        "type",
        "websocket.close"
    );
    if (!send_dict)
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (code)
    {
        if (
            PyDict_SetItemString(
                send_dict,
                "code",
                code
            ) < 0
        )
        {
            Py_DECREF(awaitable);
            Py_DECREF(send_dict);
            return NULL;
        }
    }

    if (reason)
    {
        if (
            PyDict_SetItemString(
                send_dict,
                "reason",
                reason
            ) < 0
        )
        {
            Py_DECREF(awaitable);
            Py_DECREF(send_dict);
            return NULL;
        }
    }

    PyObject *coro = PyObject_Vectorcall(
        self->send,
        (PyObject *[]) { send_dict },
        1,
        NULL
    );
    Py_DECREF(send_dict);

    if (!coro)
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (
        PyAwaitable_AWAIT(
            awaitable,
            coro
        ) < 0
    )
    {
        Py_DECREF(awaitable);
        return NULL;
    }
    self->closing = true;

    Py_DECREF(coro);
    return awaitable;
}

/*
 * Send data to the client.
 *
 * This is a Python method that accepts a string or bytes.
 */
static PyObject *
WebSocket_send(WebSocket *self, PyObject *args)
{
    /*
     * Note that this is still a private API - the Python send()
     * function in WebSocket() is responsible for wrapping it.
     * Breaking changes are allowed!
     */
    PyObject *data;

    if (
        !PyArg_ParseTuple(
            args,
            "O",
            &data
        )
    )
        return NULL;

    PyObject *awaitable = PyAwaitable_New();
    if (!awaitable)
        return NULL;

    PyObject *send_dict;
    if (PyUnicode_Check(data))
    {
        send_dict = Py_BuildValue(
            "{s:s,s:S}",
            "type",
            "websocket.send",
            "text",
            data
        );
    } else if (PyBytes_Check(data))
    {
        send_dict = Py_BuildValue(
            "{s:s,s:S}",
            "type",
            "websocket.send",
            "bytes",
            data
        );
    } else
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected string or bytes, got %R",
            Py_TYPE(data)
        );
        return NULL;
    }

    if (!send_dict)
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    PyObject *coro = PyObject_Vectorcall(
        self->send,
        (PyObject *[]) { send_dict },
        1,
        NULL
    );
    Py_DECREF(send_dict);

    if (!coro)
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (
        PyAwaitable_AWAIT(
            awaitable,
            coro
        ) < 0
    )
    {
        Py_DECREF(awaitable);
        Py_DECREF(coro);
        return NULL;
    }

    Py_DECREF(coro);
    return awaitable;
}

static PyMethodDef methods[] =
{
    {"accept", (PyCFunction) WebSocket_accept, METH_NOARGS, NULL},
    {"receive", (PyCFunction) WebSocket_receive, METH_NOARGS, NULL},
    {"close", (PyCFunction) WebSocket_close, METH_VARARGS | METH_KEYWORDS,
     NULL},
    {"send", (PyCFunction) WebSocket_send, METH_VARARGS, NULL},
    {NULL}
};

PyTypeObject WebSocketType =
{
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
    .tp_methods = methods
};
