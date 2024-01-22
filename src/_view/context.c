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
    PyObject* server;
} Context;

static PyMemberDef members[] = {
    {"scheme", T_OBJECT_EX, offsetof(Context, scheme), 0, NULL},
    {"headers", T_OBJECT_EX, offsetof(Context, headers), 0, NULL},
    {"cookies", T_OBJECT_EX, offsetof(Context, cookies), 0, NULL},
    {"http_version", T_OBJECT_EX, offsetof(Context, http_version), 0, NULL},
    {"client", T_OBJECT, offsetof(Context, client), 0, NULL},
    {"server", T_OBJECT, offsetof(Context, server), 0, NULL},
    {NULL}  /* Sentinel */
};

PyObject* Context_new(PyTypeObject* type, PyObject* args, PyObject* kwargs) {
    Context* self = (Context*) type->tp_alloc(type, 0);
    if (!self)
        return NULL;

    self->scheme = NULL;
    return (PyObject*) self;
}

static void dealloc(Context* self) {
    Py_XDECREF(self->scheme);
}

PyObject* handle_route_data(int data, PyObject* scope) {
    Context* context = (Context*) Context_new(&ContextType, NULL, NULL);
    PyObject* scheme = Py_XNewRef(PyDict_GetItemString(scope, "scheme"));
    PyObject* http_version = Py_XNewRef(PyDict_GetItemString(scope,
        "http_version"));
    PyObject* header_list = PyDict_GetItemString(scope, "headers");
    PyObject* client = PyDict_GetItemString(scope, "client"); // [host, port]
    PyObject* server = PyDict_GetItemString(scope, "server"); // [host, port/None]

    if (!scheme || !header_list || !http_version || !client || !server) {
        Py_XDECREF(scheme);
        Py_XDECREF(http_version);
        Py_DECREF(context);
        PyErr_BadASGI();
        return NULL;
    }

    context->http_version = http_version;
    context->scheme = scheme;

    if (client != Py_None) {
        if (PyList_Size(client) != 2) {
            Py_DECREF(context);
            PyErr_BadASGI();
            return NULL;
        }

        int port = PyLong_AsLong(PyList_GET_ITEM(client, 1));
        if (PyErr_Occurred()) {
            Py_DECREF(context);
            return NULL;
        }

        PyObject* string = PyUnicode_FromFormat(
            "%U:%d",
            PyList_GET_ITEM(client, 0),
            port
        );
        if (!string) {
            Py_DECREF(context);
            return NULL;
        }
        PyObject* address = PyObject_Vectorcall(
            ip_address,
            (PyObject*[]) { string },
            1,
            NULL
        );

        Py_DECREF(string);
        if (!address) {
            Py_DECREF(context);
            return NULL;
        }

        context->client = address;
    } else {
        context->client = NULL;
    }

    if (server != Py_None) {
        if (PyList_Size(server) != 2) {
            Py_DECREF(context);
            PyErr_BadASGI();
            return NULL;
        }

        PyObject* port_obj = PyList_GET_ITEM(server, 1);

        if (port_obj != Py_None) {
            int port = PyLong_AsLong(PyList_GET_ITEM(server, 1));
            if (PyErr_Occurred()) {
                Py_DECREF(context);
                return NULL;
            }

            PyObject* string = PyUnicode_FromFormat(
                "%U:%d",
                PyList_GET_ITEM(server, 0),
                port
            );
            if (!string) {
                Py_DECREF(context);
                return NULL;
            }
            PyObject* address = PyObject_Vectorcall(
                ip_address,
                (PyObject*[]) { string },
                1,
                NULL
            );

            Py_DECREF(string);
            if (!address) {
                Py_DECREF(context);
                return NULL;
            }

            context->server = address;
        } else {
            PyObject* address = PyObject_Vectorcall(
                ip_address,
                (PyObject*[]) { PyList_GET_ITEM(server, 0) },
                1,
                NULL
            );
            context->server = address;
        }
    } else {
        context->server = NULL;
    }

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
        PyObject* header = PyList_GET_ITEM(header_list, i);

        if (PyList_Size(header) != 2) {
            Py_DECREF(context);
            PyErr_BadASGI();
            return NULL;
        }

        PyObject* key_bytes = PyList_GET_ITEM(header, 0);
        PyObject* value_bytes = PyList_GET_ITEM(header, 1);
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

        PyObject* target = PyUnicode_CompareWithASCIIString(key, "cookie") ==
                           0 ? cookies : headers;
        if (PyDict_SetItem(target, key, value) < 0) {
            Py_DECREF(key);
            Py_DECREF(value);
            Py_DECREF(context);
            return NULL;
        }

        Py_DECREF(key);
        Py_DECREF(value);
    }

    return (PyObject*) context;
}


PyTypeObject ContextType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_view.Context",
    .tp_basicsize = sizeof(Context),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Context_new,
    .tp_dealloc = (destructor) dealloc,
    .tp_members = members,
};
