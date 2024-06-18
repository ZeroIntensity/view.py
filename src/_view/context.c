/*
 * view.py route context implementation
 *
 * This file provides the definition and logic of the Context() class. A context
 * essentially wraps the ASGI scope, and contains a reference to the app instance.
 *
 * It contains information that someone might find useful, such as the headers,
 * cookies, method, route, and so on. Use of the context's attributes should be
 * avoided from C, since you have the ASGI scope in C. This is, more or less, a
 * transport for passing those values to something like a route.
 *
 * Note that this also does some header parsing through the HeaderDict() class.
 *
 * The implementation of Context() is pretty simple. It's a simple extension type that
 * uses PyMemberDef with T_OBJECT or T_OBJECT_EX for all the fields.
 *
 * The object is constructed at runtime by the exported context_from_data() function,
 * which is called during route input generation. context_from_data() is responsible
 * for unpacking all the values given the ASGI scope. For convenience, the app
 * instance is stored on the object as well.
 *
 * Note that while this is part of the private _view module, fields of Context() are
 * considered to be a public API. Make changes to those with caution! They have much
 * less lenience than the rest of the C API.
 */
#include <Python.h>
#include <structmember.h> // PyMemberDef

#include <stddef.h> // offsetof

#include <view/app.h> // PyErr_BadASGI
#include <view/backport.h>
#include <view/context.h>
#include <view/headerdict.h> // headerdict_from_list
#include <view/view.h> // ip_address

typedef struct {
    PyObject_HEAD
    PyObject* app;
    PyObject* scheme;
    PyObject* headers;
    PyObject* cookies;
    PyObject* http_version;
    PyObject* client;
    PyObject* client_port;
    PyObject* server;
    PyObject* server_port;
    PyObject* method;
    PyObject* path;
} Context;

static PyMemberDef members[] = {
    {"app", T_OBJECT_EX, offsetof(Context, app), 0, NULL},
    {"scheme", T_OBJECT_EX, offsetof(Context, scheme), 0, NULL},
    {"headers", T_OBJECT_EX, offsetof(Context, headers), 0, NULL},
    {"cookies", T_OBJECT_EX, offsetof(Context, cookies), 0, NULL},
    {"http_version", T_OBJECT_EX, offsetof(Context, http_version), 0, NULL},
    {"client", T_OBJECT, offsetof(Context, client), 0, NULL},
    {"client_port", T_OBJECT, offsetof(Context, client_port), 0, NULL},
    {"server", T_OBJECT, offsetof(Context, server), 0, NULL},
    {"server_port", T_OBJECT, offsetof(Context, server_port), 0, NULL},
    {"method", T_OBJECT, offsetof(Context, method), 0, NULL},
    {"path", T_OBJECT, offsetof(Context, path), 0, NULL},
    {NULL} // Sentinel
};

/*
 * Python __repr__ for Context()
 * As of now, this is just a really long format string.
 */
static PyObject* repr(PyObject* self) {
    Context* ctx = (Context*) self;
    return PyUnicode_FromFormat(
        "Context(app=..., scheme=%R, headers=%R, cookies=%R, http_version=%R, client=%R, client_port=%R, server=%R, server_port=%R, method=%R, path=%R)",
        ctx->scheme,
        ctx->headers,
        ctx->cookies,
        ctx->http_version,
        ctx->client,
        ctx->client_port,
        ctx->server,
        ctx->server_port,
        ctx->method,
        ctx->path
    );
}

/* The Context Deallocator */
static void dealloc(Context* self) {
    Py_XDECREF(self->app);
    Py_XDECREF(self->scheme);
    Py_XDECREF(self->headers);
    Py_XDECREF(self->cookies);
    Py_XDECREF(self->http_version);
    Py_XDECREF(self->client);
    Py_XDECREF(self->client_port);
    Py_XDECREF(self->server);
    Py_XDECREF(self->server_port);
    Py_XDECREF(self->method);
    Py_XDECREF(self->path);
    Py_TYPE(self)->tp_free((PyObject*) self);
}

/*
 * Initializer for the Context() class.
 *
 * This shouldn't be called outside of this file, as the app
 * generates Context() inputs through the exported context_from_data()
 *
 * Again, only the *attributes* for Context() are considered public.
 * This can change at any time!
 */
static PyObject* Context_new(
    PyTypeObject* type,
    PyObject* args,
    PyObject* kwargs
) {
    Context* self = (Context*) type->tp_alloc(
        type,
        0
    );
    if (!self)
        return NULL;

    return (PyObject*) self;
}

/*
 * The actual interface for generating a Context() instance at runtime.
 *
 * This doesn't really do much other than unpack values from
 * the ASGI scope and store them in the proper attributes, with
 * the exception of calling headerdict_from_list() on the headers.
 *
 * Private API - no access from Python and unstable.
 */
PyObject* context_from_data(PyObject* app, PyObject* scope) {
    Context* context = (Context*) Context_new(
        &ContextType,
        NULL,
        NULL
    );
    PyObject* scheme = Py_XNewRef(
        PyDict_GetItemString(
            scope,
            "scheme"
        )
    );
    PyObject* http_version = Py_XNewRef(
        PyDict_GetItemString(
            scope,
            "http_version"
        )
    );
    PyObject* method = Py_XNewRef(
        PyDict_GetItemString(
            scope,
            "method"
        )
    );
    PyObject* path = Py_XNewRef(
        PyDict_GetItemString(
            scope,
            "path"
        )
    );
    PyObject* header_list = PyDict_GetItemString(
        scope,
        "headers"
    );
    PyObject* client = PyDict_GetItemString(
        scope,
        "client"
    ); // [host, port]
    PyObject* server = PyDict_GetItemString(
        scope,
        "server"
    ); // [host, port/None]

    if (!scheme || !header_list || !http_version || !client || !server ||
        !path || !method) {
        Py_XDECREF(scheme);
        Py_XDECREF(http_version);
        Py_XDECREF(path);
        Py_XDECREF(client);
        Py_XDECREF(method);
        Py_DECREF(context);
        PyErr_BadASGI();
        return NULL;
    }

    context->http_version = http_version;
    context->scheme = scheme;
    context->method = method;
    context->path = path;

    if (client != Py_None) {
        if (PyTuple_Size(client) != 2) {
            Py_DECREF(context);
            Py_DECREF(client);
            Py_DECREF(server);
            Py_DECREF(path);
            Py_DECREF(method);
            Py_DECREF(http_version);
            PyErr_BadASGI();
            return NULL;
        }

        context->client_port = Py_NewRef(
            PyTuple_GET_ITEM(
                client,
                1
            )
        );
        if (PyErr_Occurred()) {
            Py_DECREF(context);
            Py_DECREF(client);
            Py_DECREF(server);
            Py_DECREF(path);
            Py_DECREF(method);
            Py_DECREF(http_version);
            return NULL;
        }

        PyObject* address = PyObject_Vectorcall(
            ip_address,
            (PyObject*[]) {
            PyTuple_GET_ITEM(client, 0)
        },
            1,
            NULL
        );

        if (!address) {
            Py_DECREF(context);
            Py_DECREF(client);
            Py_DECREF(server);
            Py_DECREF(path);
            Py_DECREF(method);
            Py_DECREF(http_version);
            return NULL;
        }

        context->client = address;
    } else context->client = NULL;

    if (server != Py_None) {
        if (PyTuple_Size(server) != 2) {
            Py_DECREF(context);
            Py_DECREF(client);
            Py_DECREF(server);
            Py_DECREF(path);
            Py_DECREF(method);
            Py_DECREF(http_version);
            Py_XDECREF(context->client);
            PyErr_BadASGI();
            return NULL;
        }

        context->server_port = Py_NewRef(
            PyTuple_GET_ITEM(
                server,
                1
            )
        );
        // no idea what uncrustify is smoking but lets roll with it
        PyObject* address = PyObject_Vectorcall(
            ip_address,
            (PyObject*[]) {
            PyTuple_GET_ITEM(
                server,
                0
            )
        },
            1,
            NULL
        );
        if (!address) {
            Py_DECREF(context);
            Py_DECREF(client);
            Py_DECREF(server);
            Py_DECREF(path);
            Py_DECREF(method);
            Py_DECREF(http_version);
            Py_XDECREF(context->client);
            return NULL;
        }
        context->server = address;
    } else context->server = NULL;

    PyObject* cookies = PyDict_New();

    if (!cookies) {
        Py_DECREF(context);
        Py_DECREF(context);
        Py_DECREF(client);
        Py_DECREF(server);
        Py_DECREF(path);
        Py_DECREF(method);
        Py_DECREF(http_version);
        Py_XDECREF(context->client);
        Py_XDECREF(context->server);
        return NULL;
    }

    context->cookies = cookies;
    context->headers = headerdict_from_list(header_list);
    if (!context->headers) {
        Py_DECREF(context);
        Py_DECREF(context);
        Py_DECREF(client);
        Py_DECREF(server);
        Py_DECREF(path);
        Py_DECREF(method);
        Py_DECREF(http_version);
        Py_XDECREF(context->client);
        Py_XDECREF(context->server);
        Py_DECREF(cookies);
        return NULL;
    }
    context->app = Py_NewRef(app);
    return (PyObject*) context;
}

PyTypeObject ContextType = {
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.Context",
    .tp_basicsize = sizeof(Context),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Context_new,
    .tp_dealloc = (destructor) dealloc,
    .tp_members = members,
    .tp_repr = repr
};
