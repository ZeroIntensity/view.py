#include <view/context.h>
#include <view/map.h>

typedef struct {
    PyObject_HEAD
    map* cookies;
    map* headers;
    map* res_cookies;
} Context;

static PyObject* new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    Context* self = (Context*) type->tp_alloc(
        type,
        0
    );
    if (!self) return NULL;
    self->cookies = map_new(
        2,
        free
    );

    return (PyObject*) self;
}

static PyObject* repr(PyObject* self) {
    return PyUnicode_FromFormat(
        "<view context at %p>",
        self
    );
}

static PyObject* cookie(Context* self, PyObject* args) {
    char* key;
    char* value;

    if (!PyArg_ParseTuple(
        args,
        "ss",
        &key,
        &value
        )) return NULL;

    map_set(
        self->cookies,
        key,
        value
    );
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"cookie", (PyCFunction) cookie, METH_VARARGS, NULL},
    {NULL}
};

PyTypeObject ContextType = {
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.Context",
    .tp_basicsize = sizeof(Context),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = new,
    .tp_repr = repr,
    .tp_methods = methods
};
