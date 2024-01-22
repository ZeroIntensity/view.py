#include <view/context.h>
#include <Python.h>
#include <structmember.h>
#include <stddef.h> // offsetof

typedef struct {
    PyObject_HEAD
    PyObject* scheme;
} Context;

static PyMemberDef members[] = {
    {"scheme", T_OBJECT, offsetof(Context, scheme), 0, NULL},
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
