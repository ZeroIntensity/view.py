#include <view/view.h>
#include <Python.h>

typedef struct {
    PyObject_HEAD
    type_info** codes;
    Py_ssize_t codes_len;
    PyObject* json_parser;
} TCPublic;

static void dealloc(TCPublic* self) {
    free_type_codes(
        self->codes,
        self->codes_len
    );
    Py_DECREF(self->json_parser);
    Py_TYPE(self)->tp_free((PyObject*) self);
}

static PyObject* new(PyTypeObject* type, PyObject* args, PyObject* kwargs) {
    TCPublic* self = (TCPublic*) type->tp_alloc(
        type,
        0
    );
    if (!self)
        return NULL;

    return (PyObject*) self;
}

static PyObject* cast_from_typecodes_public(PyObject* self, PyObject* args) {
    TCPublic* tc = (TCPublic*) self;
    PyObject* obj;
    int allow_cast;

    if (!PyArg_ParseTuple(
        args,
        "Op",
        &obj,
        &allow_cast
        ))
        return NULL;

    PyObject* res = cast_from_typecodes(
        tc->codes,
        tc->codes_len,
        obj,
        tc->json_parser,
        allow_cast
    );
    if (!res) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "cast_from_typecodes returned NULL"
        );
        return NULL;
    }

    return res;
}

static PyObject* compile(PyObject* self, PyObject* args) {
    TCPublic* tc = (TCPublic*) self;
    PyObject* list;
    PyObject* json_parser;

    if (!PyArg_ParseTuple(
        args,
        "OO",
        &list,
        &json_parser
        ))
        return NULL;

    if (!PySequence_Check(list)) {
        PyErr_SetString(
            PyExc_TypeError,
            "expected a sequence"
        );
        return NULL;
    }

    Py_ssize_t size = PySequence_Size(list);
    if (size < 0)
        return NULL;

    type_info** info = build_type_codes(
        list,
        size
    );
    tc->codes = info;
    tc->codes_len = size;
    tc->json_parser = Py_NewRef(json_parser);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"_compile", (PyCFunction) compile, METH_VARARGS, NULL},
    {"_cast", (PyCFunction) cast_from_typecodes_public, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};


PyTypeObject TCPublicType = {
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.TCPublic",
    .tp_basicsize = sizeof(TCPublic),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = new,
    .tp_dealloc = (destructor) dealloc,
    .tp_methods = methods,
};
