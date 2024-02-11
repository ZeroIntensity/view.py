#include <view/view.h>
#include <Python.h>
#include <structmember.h>
#include <stddef.h> // offsetof

typedef struct {
    PyObject_HEAD
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
    {"scheme", T_OBJECT_EX, offsetof(
        Context,
        scheme
     ), 0, NULL},
    {"headers", T_OBJECT_EX, offsetof(
        Context,
        headers
     ), 0, NULL},
    {"cookies", T_OBJECT_EX, offsetof(
        Context,
        cookies
     ), 0, NULL},
    {"http_version", T_OBJECT_EX, offsetof(
        Context,
        http_version
     ), 0, NULL},
    {"client", T_OBJECT, offsetof(
        Context,
        client
     ), 0, NULL},
    {"client_port", T_OBJECT, offsetof(
        Context,
        client_port
     ), 0, NULL},
    {"server", T_OBJECT, offsetof(
        Context,
        server
     ), 0, NULL},
    {"server_port", T_OBJECT, offsetof(
        Context,
        server_port
     ), 0, NULL},
    {"method", T_OBJECT, offsetof(
        Context,
        method
     ), 0, NULL},
    {"path", T_OBJECT, offsetof(
        Context,
        path
     ), 0, NULL},
    {NULL}  /* Sentinel */
};

static PyObject* repr(PyObject* self) {
    Context* ctx = (Context*) self;
    return PyUnicode_FromFormat(
        "Context(scheme=%R, headers=%R, cookies=%R, http_version=%R, client=%R, client_port=%R, server=%R, server_port=%R, method=%R, path=%R)",
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


static void dealloc(Context* self) {
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

PyObject* context_from_data(PyObject* scope) {
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
    );                                                        // [host, port]
    PyObject* server = PyDict_GetItemString(
        scope,
        "server"
    );                                                        // [host, port/None]

    if (!scheme || !header_list || !http_version || !client || !server ||
        !path || !method) {
        Py_XDECREF(scheme);
        Py_XDECREF(http_version);
        Py_XDECREF(path);
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
            return NULL;
        }

        PyObject* address = PyObject_Vectorcall(
            ip_address,
            (PyObject*[]) { PyTuple_GET_ITEM(
                client,
                0
                            ) },
            1,
            NULL
        );

        if (!address) {
            Py_DECREF(context);
            return NULL;
        }

        context->client = address;
    } else context->client = NULL;
    if (server != Py_None) {
        if (PyTuple_Size(server) != 2) {
            Py_DECREF(context);
            PyErr_BadASGI();
            return NULL;
        }

        context->server_port = Py_NewRef(
            PyTuple_GET_ITEM(
                server,
                1
            )
        );
        PyObject* address = PyObject_Vectorcall(
            ip_address,
            (PyObject*[]) { PyTuple_GET_ITEM(
                server,
                0
                            ) },
            1,
            NULL
        );
        context->server = address;
    } else context->server = NULL;

    PyObject* headers = PyDict_New();

    if (!headers) {
        Py_DECREF(context);
        return NULL;
    }

    context->headers = headers;
    PyObject* cookies = PyDict_New();

    if (!cookies) {
        Py_DECREF(context);
        return NULL;
    }

    context->cookies = cookies;

    for (int i = 0; i < PyList_GET_SIZE(header_list); i++) {
        PyObject* header = PyList_GET_ITEM(
            header_list,
            i
        );

        if (PyTuple_Size(header) != 2) {
            Py_DECREF(context);
            PyErr_BadASGI();
            return NULL;
        }

        PyObject* key_bytes = PyTuple_GET_ITEM(
            header,
            0
        );
        PyObject* value_bytes = PyTuple_GET_ITEM(
            header,
            1
        );
        PyObject* key = PyUnicode_FromEncodedObject(
            key_bytes,
            "utf8",
            "strict"
        );
        PyObject* value = PyUnicode_FromEncodedObject(
            value_bytes,
            "utf8",
            "strict"
        );

        if (!key || !value) {
            Py_XDECREF(key);
            Py_XDECREF(value);
            Py_DECREF(context);
            return NULL;
        }

        if (PyUnicode_CompareWithASCIIString(
            key,
            "cookie"
            ) == 0) {
            PyObject* d = PyUnicode_FromString("=");

            if (!d) {
                Py_DECREF(context);
                Py_DECREF(key);
                Py_DECREF(value);
                return NULL;
            }

            PyObject* parts = PyUnicode_Partition(
                value,
                d
            );
            PyObject* cookie_key = PyTuple_GET_ITEM(
                parts,
                0
            );
            PyObject* cookie_value = PyTuple_GET_ITEM(
                parts,
                2
            );

            if (PyDict_SetItem(
                cookies,
                cookie_key,
                cookie_value
                ) < 0) {
                Py_DECREF(cookie_key);
                Py_DECREF(cookie_value);
                Py_DECREF(parts);
                Py_DECREF(d);
                Py_DECREF(context);
                Py_DECREF(key);
                Py_DECREF(value);
                return NULL;
            }

            Py_DECREF(parts);
            Py_DECREF(d);
        } else {
            if (PyDict_SetItem(
                headers,
                key,
                value
                ) < 0) {
                Py_DECREF(key);
                Py_DECREF(value);
                Py_DECREF(context);
                return NULL;
            }
        }

        Py_DECREF(key);
        Py_DECREF(value);
    }

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
