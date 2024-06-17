#include <Python.h>
#include <structmember.h> // PyMemberDef

#include <stdbool.h>
#include <stddef.h> // offsetof

#include <view/backport.h>
#include <view/map.h>
#include <view/headerdict.h>

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

static int set_item(HeaderDict* self, PyObject* key, PyObject* value) {
    if (!PyUnicode_CheckExact(value)) {
        PyErr_Format(PyExc_TypeError,
            "expected header dict index to be a string, not %R", value);
        return -1;
    }

    const char* key_str = PyUnicode_AsUTF8(value);
    if (!key_str)
        return -1;

    header_item* item = map_get(self->headers, key_str);
    if (!item) {
        // item is not set, set it
        item = header_item_new(value);
        if (!item)
            return -1;

        map_set(self->headers, key_str, item);
        return 0;
    }

    if (item->is_list) {
        if (PyList_Append(item->value, value) < 0)
            return -1;
        return 0;
    }

    PyObject* list = PyList_New(2);
    if (!list)
        return -1;

    PyList_SET_ITEM(list, 0, item->value);
    PyList_SET_ITEM(list, 1, Py_NewRef(value));
    item->value = list;

    return 0;
}

static Py_ssize_t get_length(HeaderDict* self) {
    return self->headers->len;
}

PyObject* headerdict_from_list(PyObject* list) {
    HeaderDict* hd = (HeaderDict*) HeaderDict_new(&HeaderDictType, NULL, NULL);
    if (!hd)
        return NULL;

    Py_ssize_t size = PyList_GET_SIZE(list);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject* tup = PyList_GET_ITEM(list, i);
        PyObject* key = PyTuple_GET_ITEM(tup, 0);
        PyObject* value = PyTuple_GET_ITEM(tup, 1);

        const char* key_str = PyBytes_AsString(key);
        if (!key_str) {
            Py_DECREF(hd);
            return NULL;
        }

        PyObject* value_str = PyUnicode_FromEncodedObject(value, "utf8",
            "strict");
        if (!value_str) {
            Py_DECREF(hd);
            return NULL;
        }

        header_item* item = header_item_new(value);
        if (!item) {
            Py_DECREF(hd);
            return NULL;
        }

        map_set(hd->headers, key_str, item);
    }

    return (PyObject*) hd;
}

static PyMappingMethods mapping_methods = {
    .mp_subscript = (binaryfunc) get_item,
    .mp_ass_subscript = (objobjargproc) set_item,
    .mp_length = (lenfunc) get_length
};

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
