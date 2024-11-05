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
#include <view/request.h>
#include <view/util.h>

#define LOAD_ROUTE(target) \

static inline PyObject *
get_scope_item(PyObject *scope, const char *name)
{
    PyObject *res = PyDict_GetItemString(scope, name);
    if (View_UNLIKELY(res == NULL))
    {
        PyErr_Format(PyExc_SystemError, "ASGI scope is missing '%s'", name);
        return NULL;
    }

    return res;
}

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
ViewApp_Init(PyObject *self, PyObject *args, PyObject *kwds)
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

static void
ViewApp_Dealloc(ViewApp *self)
{
    ViewApp_ClearErrorState(&self->errors);

    // Lifespan
    Py_CLEAR(self->lifecycle.startup);
    Py_CLEAR(self->lifecycle.cleanup);

    Py_TYPE(self)->tp_free(self);
}

ViewRoute *
ViewApp_FindRoute(ViewRequest *request)
{
    assert(request != NULL);
    ViewApp *app = request->app;
    PyObject *path = request->common.unparsed_path;
    assert(app != NULL);
    assert(path != NULL);
    const char *str = PyUnicode_AsUTF8(path);
    if (View_UNLIKELY(str == NULL))
    {
        return NULL;
    }

#define METHOD(value)                                           \
        do {                                                    \
            if (!strcmp(str, #value)) {                         \
                return ViewMap_Get(app->routes. ## value, str); \
            }                                                   \
        } while (0)
    METHOD(get);

    // TODO: Optimize this lookup
#undef METHOD
}

/*
 * view.py ASGI implementation. This is where the magic happens!
 *
 * This is accessible via asgi_app_entry() in Python.
 *
 */
View_HOT static PyObject *
ViewApp_App(
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

    // Everything returned by get_scope_item() is a borrowed reference
    PyObject *tp = get_scope_item(
        scope,
        "type"
    );

    if (View_UNLIKELY(tp == NULL))
    {
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

    /*
     * At this point, we know it's a real HTTP or WebSocket request.
     * Get the URL route from the scope.
     */
    PyObject *url_route_object = get_scope_item(
        scope,
        "path"
    );

    if (View_UNLIKELY(url_route_object == NULL))
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    const char *url_route = PyUnicode_AsUTF8(url_route_object);
    if (View_UNLIKELY(url_route == NULL))
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    /*
     * Now, it's time to construct our request.
     * This will hold all the data for the lifetime of the connection.
     */
    ViewRequest *request = View_AllocStructureCast(ViewRequest);
    if (View_UNLIKELY(request == NULL))
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    /* Store a (borrowed) reference to the app */
    request->app = self;

    /* Store the request ASGI data */
    request->asgi.awaitable = awaitable; // This steals our own reference
    request->asgi.scope = Py_NewRef(scope);
    request->asgi.receive = Py_NewRef(receive);
    request->asgi.send = Py_NewRef(send);

    /* Store common request data, such as the headers or query string */
    request->common.unparsed_path = Py_NewRef(url_route_object);
    request->common.headers = get_scope_item(scope, "headers");
    if (View_UNLIKELY(request->common.headers == NULL))
    {
        ViewRequest_Free(request);
        return NULL;
    }

    request->common.query = get_scope_item(scope, "query_string");
    if (View_UNLIKELY(request->common.query == NULL))
    {
        ViewRequest_Free(request);
        return NULL;
    }

    /*
     * Now, find out what route we're going to.
     */
    ViewRoute *route = ViewApp_FindRoute(request);
    if (route == NULL)
    {
        // Something failed, or it doesn't exist.
        if (View_UNLIKELY(PyErr_Occurred() != NULL))
        {
            ViewRequest_Free(request);
            return NULL;
        }

        /* TODO: Send a 404 */
    }

    if (PyUnicode_CompareWithASCIIString(tp, "http"))
    {
        request->type = HTTP;
        /*
         * TODO: Go for HTTP
         */
    } else
    {
        assert(PyUnicode_CompareWithASCIIString(tp, "websocket"));
        request->type = WEBSOCKET;
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

static PyMethodDef ViewApp_Methods[] =
{
    {"asgi_app_entry", (PyCFunction) ViewApp_App, METH_FASTCALL, NULL},
    {"_get", (PyCFunction) get, METH_VARARGS, NULL},
    {"_post", (PyCFunction) post, METH_VARARGS, NULL},
    {"_put", (PyCFunction) put, METH_VARARGS, NULL},
    {"_patch", (PyCFunction) patch, METH_VARARGS, NULL},
    {"_delete", (PyCFunction) delete, METH_VARARGS, NULL},
    {"_options", (PyCFunction) options, METH_VARARGS, NULL},
    {"_websocket", (PyCFunction) websocket, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

PyTypeObject ViewApp_Type =
{
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.ViewApp",
    .tp_basicsize = sizeof(ViewApp),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_init = (initproc) ViewApp_Init,
    .tp_methods = ViewApp_Methods,
    .tp_new = ViewApp_New,
    .tp_dealloc = (destructor) ViewApp_Dealloc
};
