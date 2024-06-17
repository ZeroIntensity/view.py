#include <Python.h>
#include <structmember.h> // PyMemberDef

#include <stdbool.h>
#include <stddef.h> // offsetof

#include <view/backport.h>
#include <view/map.h>

typedef struct {
    bool is_list;
    PyObject* value;
} header_item;

void header_item_free(header_item* item) {
    Py_DECREF(item->value);
    PyMem_Free(item);
}

header_item* header_item_new(PyObject* value) {
    header_item* item = PyMem_Malloc(sizeof(header_item));
    if (!item)
        return NULL;

    item->is_list = false;
    item->value = Py_NewRef(value);
    return item;
}

typedef struct {
    PyObject_HEAD
    map* headers;
} HeaderDict;

static PyObject* repr(PyObject* self) {
    return PyUnicode_FromFormat(
        "HeaderDict({})"
    );
}


static void dealloc(HeaderDict* self) {
    if (self->headers)
        map_free(self->headers);
    Py_TYPE(self)->tp_free((PyObject*) self);
}

static PyObject* HeaderDict_new(
    PyTypeObject* type,
    PyObject* args,
    PyObject* kwargs
) {
    HeaderDict* self = (HeaderDict*) type->tp_alloc(
        type,
        0
    );
    if (!self)
        return NULL;

    self->headers = map_new(4, (map_free_func) header_item_free);
    if (!self->headers) {
        Py_DECREF(self);
        return NULL;
    }
    return (PyObject*) self;
}

static PyObject* get_item(HeaderDict* self, PyObject* value) {
    if (!PyUnicode_CheckExact(value)) {
        PyErr_Format(PyExc_TypeError,
            "expected header dict index to be a string, not %R", value);
        return NULL;
    }

    const char* key = PyUnicode_AsUTF8(value);
    if (!key)
        return NULL;

    header_item* item = map_get(self->headers, key);
    if (item == NULL) {
        PyErr_SetObject(PyExc_KeyError, value);
        return NULL;
    }

    return Py_NewRef(item->value);
}

PyTypeObject HeaderDictType = {
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.HeaderDict",
    .tp_basicsize = sizeof(HeaderDict),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = HeaderDict_new,
    .tp_dealloc = (destructor) dealloc,
    .tp_repr = repr
};
