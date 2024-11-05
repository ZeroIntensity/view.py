/*
 * view.py ASGI app implementation
 *
 * This file contains the ViewApp class, which is the base class for the App class.
 * All the actual ASGI calls are here. The ASGI app location is under the asgi_app_entry() method.
 *
 * The view.py ASGI app should *never* raise an exception (in a perfect world, at least). All errors
 * should be handled accordingly, and a proper HTTP response should be sent back in all cases, regardless of what happened.
 *
 * The lifecycle of a request is as follows:
 *
 * - Receive ASGI values (scope, receive(), and send())
 * - If it's a lifespan call, start the lifespan protocol.
 * - If not, extract the path and method from the scope.
 * - If it's an HTTP request:
 *       * Search the corresponding method map with the route.
 *       * If it's not found, check if the app has path parameters.
 *           > If not, return a 404.
 *           > If it does, defer to the path parts API (very unstable and buggy).
 *       * If it is found, check if the route has inputs (data inputs, query parameters, and body parameters).
 *           > If it does, defer to the proper handler function.
 *           > If not, we can just call it right now, and send the result to the results API.
 * - If it's a WebSocket connection:
 *       * Search the WebSocket map with the route.
 *       * If it's not found, check if the app has path parameters.
 *           > If not, return a 404, but explicitly mark it as a WebSocket rejection (websocket.http.response)
 *           > If it does, defer to the path parts API (very unstable and buggy). This is not implemented yet!
 *       * Defer to the proper handler function. A WebSocket route always has at least one input.
 */
#include <Python.h>

#include <pyawaitable.h>
#include <stdbool.h>
#include <signal.h>

#include <view/app.h>
#include <view/util.h>

#define LOAD_ROUTE(target) \

/*
 * Allocate and initialize a new ViewApp object.
 * This builds all the route tables, and any other field on the ViewApp struct.
 */
static PyObject *
ViewApp_New(PyTypeObject *tp, PyObject *args, PyObject *kwds)
{
    ViewApp *self = (ViewApp *) tp->tp_alloc(
        tp,
        0
    );

    return (PyObject *) self;
}

static int
init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyErr_SetString(
        PyExc_TypeError,
        "ViewApp is not constructable"
    );
    return -1;
}

/*
 * ASGI lifespan implementation.
 */
static int
lifespan(PyObject *awaitable, PyObject *result)
{
    return 0;
}

/* The ViewApp deallocator. */
static void
dealloc(ViewApp *self)
{
    ViewApp_ClearErrorState(&self->errors);

    // Lifespan
    Py_CLEAR(self->lifecycle.startup);
    Py_CLEAR(self->lifecycle.cleanup);

    Py_TYPE(self)->tp_free(self);
}

/*
 * view.py ASGI implementation. This is where the magic happens!
 *
 * This is accessible via asgi_app_entry() in Python.
 *
 */
View_HOT static PyObject *
app(
    ViewApp *self,
    PyObject * const *args,
    Py_ssize_t nargs
)
{
    /*
     * All HTTP and WebSocket connections start here. This function is responsible for
     * looking up loaded routes, calling PyAwaitable, and so on.
     *
     * Note that a lot of things aren't actually implemented here, such as route handling, but
     * it's all sort of stitched together in this function.
     *
     * As mentioned in the top comment, this should always send some sort
     * of response back to the user, regardless of how badly things went.
     *
     * For example, if an error occurred somewhere, this should sent
     * back a 500 (assuming that an exception handler doesn't exist).
     *
     * We don't want to let the ASGI server do it, because then we're
     * missing out on the chance to call an error handler or log what happened.
     */

    // We can assume that there will be three arguments.
    // If there aren't, then something is seriously wrong!
    assert(nargs == 3);
    PyObject *scope = args[0];
    PyObject *receive = args[1];
    PyObject *send = args[2];

    // Borrowed reference
    PyObject *tp = PyDict_GetItemString(
        scope,
        "type"
    );

    if (View_UNLIKELY(tp == NULL))
    {
        PyErr_BadASGI();
        return NULL;
    }

    PyObject *awaitable = PyAwaitable_New();
    if (View_UNLIKELY(awaitable == NULL))
    {
        return NULL;
    }

    if (View_UNLIKELY(PyUnicode_CompareWithASCIIString(tp, "lifespan")))
    {
        /* TODO: Lifespan */
    }

    PyObject *url_route_object = PyDict_GetItemString(
        scope,
        "path"
    );

    if (View_UNLIKELY(url_route_object == NULL))
    {
        Py_DECREF(awaitable);
        PyErr_BadASGI();
        return NULL;
    }

    const char *url_route = PyUnicode_AsUTF8(url_route_object);
    if (View_UNLIKELY(url_route == NULL))
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyUnicode_CompareWithASCIIString(tp, "http"))
    {
        /*
         * TODO: Go for HTTP
         */
    } else
    {
        assert(PyUnicode_CompareWithASCIIString(tp, "websocket"));
        /*
         * TODO: Go for WebSocket
         */
    }

    return awaitable;
}

/*
 * These are all loader functions that allocate a route structure and store
 * it on the corresponding route table.
 */
ROUTE(get);
ROUTE(post);
ROUTE(patch);
ROUTE(put);
ROUTE(delete);
ROUTE(options);

/*
 * Loader function for WebSockets.
 * We have a special case for WebSocket routes - the `is_http` field is set to false.
 */
static PyObject *
websocket(ViewApp *self, PyObject *args)
{
    LOAD_ROUTE(websocket);
    r->is_http = false;
    Py_RETURN_NONE;
}

/*
 * Adds a global error handler to the app.
 *
 * Note that this is for *status* codes only, not exceptions!
 * For example, if a route returned 400 without raising an exception,
 * then the handler for error 400 would be called.
 *
 * This is more or less undocumented, and subject to change.
 */
static PyObject *
err_handler(ViewApp *self, PyObject *args)
{
    PyObject *handler;
    int status_code;

    if (
        !PyArg_ParseTuple(
            args,
            "iO",
            &status_code,
            &handler
        )
    ) return NULL;

    if (status_code < 400 || status_code > 511)
    {
        PyErr_Format(
            PyExc_ValueError,
            "%d is not a valid status code",
            status_code
        );
        return NULL;
    }

    if (status_code >= 500)
    {
        self->server_errors[status_code - 500] = Py_NewRef(handler);
    } else
    {
        uint16_t index = hash_client_error(status_code);
        if (index == 600)
        {
            PyErr_Format(
                PyExc_ValueError,
                "%d is not a valid status code",
                status_code
            );
            return NULL;
        }
        self->client_errors[index] = Py_NewRef(handler);
    }

    Py_RETURN_NONE;
}

/*
 * Adds a global exception handler to the app.
 *
 * This is similar to err_handler(), but this
 * catches exceptions instead of error response codes.
 */
static PyObject *
exc_handler(ViewApp *self, PyObject *args)
{
    PyObject *dict;
    if (
        !PyArg_ParseTuple(
            args,
            "O!",
            &PyDict_Type,
            &dict
        )
    ) return NULL;
    if (self->exceptions)
    {
        PyDict_Merge(
            self->exceptions,
            dict,
            1
        );
    } else
    {
        self->exceptions = Py_NewRef(dict);
    }

    Py_RETURN_NONE;
}

static PyMethodDef methods[] =
{
    {"asgi_app_entry", (PyCFunction) app, METH_FASTCALL, NULL},
    {"_get", (PyCFunction) get, METH_VARARGS, NULL},
    {"_post", (PyCFunction) post, METH_VARARGS, NULL},
    {"_put", (PyCFunction) put, METH_VARARGS, NULL},
    {"_patch", (PyCFunction) patch, METH_VARARGS, NULL},
    {"_delete", (PyCFunction) delete, METH_VARARGS, NULL},
    {"_options", (PyCFunction) options, METH_VARARGS, NULL},
    {"_websocket", (PyCFunction) websocket, METH_VARARGS, NULL},
    {"_err", (PyCFunction) err_handler, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

PyTypeObject ViewAppType =
{
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
