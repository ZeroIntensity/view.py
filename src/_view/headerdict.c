#include <Python.h>
#include <structmember.h> // PyMemberDef

#include <stdbool.h>
#include <stddef.h> // offsetof

#include <view/backport.h>
#include <view/map.h>
#include <view/headerdict.h>
#include <view/results.h> // pymem_strdup
#include <view/view.h> // COLD

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

/*
 * This creates a copy of the object as a dictionary.
 * It's not perfect, but this function won't really get called in production,
 * so we can cheat a little bit here.
 */
static PyObject* repr(HeaderDict* self) {
    PyObject* dict_repr = PyDict_New();
    if (!dict_repr)
        return NULL;

    for (Py_ssize_t i = 0; i < self->headers->capacity; ++i) {
        pair* p = self->headers->items[i];
        if (!p)
            continue;

        header_item* it = p->value;
        if (PyDict_SetItemString(dict_repr, p->key, it->value) < 0) {
            Py_DECREF(dict_repr);
            return NULL;
        };
    }

    return PyUnicode_FromFormat(
        "HeaderDict(%R)",
        dict_repr
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

// For debugging
COLD static void print_header_item(header_item* item) {
    PyObject_Print(item->value, stdout, Py_PRINT_RAW);
}

static PyObject* get_item(HeaderDict* self, PyObject* value) {
    if (!PyUnicode_CheckExact(value)) {
        PyErr_Format(PyExc_TypeError,
            "expected header dict index to be a string, not %R", value);
        return NULL;
    }

    Py_ssize_t key_size;
    const char* const_key_str = PyUnicode_AsUTF8AndSize(value, &key_size);
    if (!const_key_str)
        return NULL;

    char* key_str = pymem_strdup(const_key_str, key_size);
    if (!key_str)
        return NULL;

    // make it lower case
    for (Py_ssize_t i = 0; key_str[i]; ++i) {
        key_str[i] = tolower(key_str[i]);
    }

    header_item* item = map_get(self->headers, key_str);
    PyMem_Free(key_str);
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

    Py_ssize_t key_size;
    const char* const_key_str = PyUnicode_AsUTF8AndSize(key, &key_size);
    if (!const_key_str)
        return -1;

    char* key_str = pymem_strdup(const_key_str, key_size);
    if (!key_str)
        return -1;

    // make it lower case
    for (Py_ssize_t i = 0; key_str[i]; ++i) {
        key_str[i] = tolower(key_str[i]);
    }

    header_item* item = map_get(self->headers, key_str);
    if (!item) {
        // item is not set, set it
        item = header_item_new(value);
        if (!item) {
            PyMem_Free(key_str);
            return -1;
        }

        map_set(self->headers, key_str, item);
        PyMem_Free(key_str);
        return 0;
    }
    PyMem_Free(key_str);

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
    item->is_list = 1;

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

        Py_ssize_t key_size;
        char* const_key_str;
        if (PyBytes_AsStringAndSize(key, &const_key_str, &key_size) < 0) {
            Py_DECREF(hd);
            return NULL;
        }

        char* key_str = pymem_strdup(const_key_str, key_size);
        if (!key_str) {
            Py_DECREF(hd);
            return NULL;
        }

        // make it lower case
        for (Py_ssize_t i = 0; key_str[i]; ++i) {
            key_str[i] = tolower(key_str[i]);
        }

        PyObject* value_str = PyUnicode_FromEncodedObject(value, "utf8",
            "strict");
        if (!value_str) {
            PyMem_Free(key_str);
            Py_DECREF(hd);
            return NULL;
        }

        header_item* item = header_item_new(value_str);
        if (!item) {
            PyMem_Free(key_str);
            Py_DECREF(hd);
            return NULL;
        }

        map_set(hd->headers, key_str, item);
        PyMem_Free(key_str);
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
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = HeaderDict_new,
    .tp_dealloc = (destructor) dealloc,
    .tp_repr = (reprfunc) repr,
    .tp_as_mapping = &mapping_methods
};
