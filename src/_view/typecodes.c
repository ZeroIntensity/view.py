#include <Python.h>
#include <stdbool.h> // bool

#include <view/backport.h>
#include <view/inputs.h> // route_input
#include <view/routing.h> // route
#include <view/typecodes.h>
#include <view/view.h> // VIEW_FATAL

#define CHECK(flags) ((typecode_flags & (flags)) == (flags))
#define TYPECODE_ANY 0
#define TYPECODE_STR 1
#define TYPECODE_INT 2
#define TYPECODE_BOOL 3
#define TYPECODE_FLOAT 4
#define TYPECODE_DICT 5
#define TYPECODE_NONE 6
#define TYPECODE_CLASS 7
#define TYPECODE_CLASSTYPES 8
#define TYPECODE_LIST 9
#define TC_VERIFY(typeobj) if (typeobj( \
                    value \
                    )) { \
                    verified = true; \
                } break;

static void free_type_info(type_info* ti) {
    Py_XDECREF(ti->ob);
    if ((intptr_t) ti->df > 0) Py_DECREF(ti->df);
    for (int i = 0; i < ti->children_size; i++) {
        free_type_info(ti->children[i]);
    }
}

void free_type_codes(type_info** codes, Py_ssize_t len) {
    for (Py_ssize_t i = 0; i < len; i++)
        free_type_info(codes[i]);
}

static inline int bad_input(const char* name) {
    PyErr_Format(
        PyExc_ValueError,
        "missing key in loader dict: %s",
        name
    );
    return -1;
}

static int verify_dict_typecodes(
    type_info** codes,
    Py_ssize_t len,
    PyObject* dict,
    PyObject* json_parser
) {
    if (!PyDict_Size(dict)) return 0;
    PyObject* iter = PyObject_GetIter(dict);
    PyObject* key;
    while ((key = PyIter_Next(iter))) {
        PyObject* value = PyDict_GetItem(
            dict,
            key
        );
        if (!value) {
            Py_DECREF(iter);
            return -1;
        }

        value = cast_from_typecodes(
            codes,
            len,
            value,
            json_parser,
            true
        );
        if (!value) return -1;
        if (PyDict_SetItem(
            dict,
            key,
            value
            ) < 0) {
            Py_DECREF(iter);
            return -1;
        }
    }

    Py_DECREF(iter);
    if (PyErr_Occurred()) {
        PyErr_Print();
        return -1;
    }

    return 0;
}


static int verify_list_typecodes(
    type_info** codes,
    Py_ssize_t len,
    PyObject* list,
    PyObject* json_parser
) {
    Py_ssize_t list_len = PySequence_Size(list);
    if (list_len == -1) return -1;
    if (list_len == 0) return 0;

    for (int i = 0; i < list_len; i++) {
        PyObject* item = PyList_GET_ITEM(
            list,
            i
        );

        item = cast_from_typecodes(
            codes,
            len,
            item,
            json_parser,
            true
        );

        if (!item) return 1;
        PyList_SET_ITEM(
            list,
            i,
            item
        );
    }

    return 0;
}

PyObject* cast_from_typecodes(
    type_info** codes,
    Py_ssize_t len,
    PyObject* item,
    PyObject* json_parser,
    bool allow_casting
) {
    if (!codes) {
        // type is Any
        if (!item) Py_RETURN_NONE;
        return item;
    };

    typecode_flag typecode_flags = 0;

    for (Py_ssize_t i = 0; i < len; i++) {
        type_info* ti = codes[i];

        switch (ti->typecode) {
        case TYPECODE_ANY: {
            return item;
        }
        case TYPECODE_STR: {
            if (!allow_casting) {
                if (PyUnicode_CheckExact(item)) {
                    return Py_NewRef(item);
                }
                return NULL;
            }
            typecode_flags |= STRING_ALLOWED;
            break;
        }
        case TYPECODE_NONE: {
            if (!allow_casting) {
                if (item == Py_None) {
                    return Py_NewRef(item);
                }
                return NULL;
            }
            typecode_flags |= NULL_ALLOWED;
            break;
        }
        case TYPECODE_INT: {
            if (PyLong_CheckExact(
                item
                )) {
                return Py_NewRef(item);
            } else if (!allow_casting) return NULL;

            PyObject* py_int = PyLong_FromUnicodeObject(
                item,
                10
            );
            if (!py_int) {
                PyErr_Clear();
                break;
            }
            return py_int;
        }
        case TYPECODE_BOOL: {
            if (PyBool_Check(
                item
                )) return Py_NewRef(item);
            else if (!allow_casting) return NULL;
            const char* str = PyUnicode_AsUTF8(item);
            PyObject* py_bool = NULL;
            if (!str) return NULL;
            if (strcmp(
                str,
                "true"
                ) == 0) {
                py_bool = Py_NewRef(Py_True);
            } else if (strcmp(
                str,
                "false"
                       ) == 0) {
                py_bool = Py_NewRef(Py_False);
            }

            if (py_bool) return py_bool;
            break;
        }
        case TYPECODE_FLOAT: {
            if (PyFloat_CheckExact(
                item
                )) return Py_NewRef(item);
            else if (!allow_casting) return NULL;
            PyObject* flt = PyFloat_FromString(item);
            if (!flt) {
                PyErr_Clear();
                break;
            }
            return flt;
        }
        case TYPECODE_DICT: {
            PyObject* obj;
            if (PyDict_Check(
                item
                )) {
                obj = Py_NewRef(item);
            } else if (!allow_casting) {
                return NULL;
            } else {
                obj = PyObject_Vectorcall(
                    json_parser,
                    (PyObject*[]) { item },
                    1,
                    NULL
                );
            }
            if (!obj) {
                PyErr_Clear();
                break;
            }
            int res = verify_dict_typecodes(
                ti->children,
                ti->children_size,
                obj,
                json_parser
            );
            if (res == -1) {
                Py_DECREF(obj);
                return NULL;
            }

            if (res == 1) {
                Py_DECREF(obj);
                break;
            }

            return obj;
        }
        case TYPECODE_CLASS: {
            if (!allow_casting) {
                if (!Py_IS_TYPE(
                    item,
                    Py_TYPE(ti->ob)
                    )) {
                    return NULL;
                }

                return Py_NewRef(item);
            }
            PyObject* kwargs = PyDict_New();
            if (!kwargs) return NULL;
            PyObject* obj;
            if (PyDict_CheckExact(item) || Py_IS_TYPE(
                item,
                Py_TYPE(ti->ob)
                )) {
                obj = Py_NewRef(item);
            } else {
                obj = PyObject_Vectorcall(
                    json_parser,
                    (PyObject*[]) { item },
                    1,
                    NULL
                );
            }

            if (!obj) {
                PyErr_Clear();
                Py_DECREF(kwargs);
                break;
            }

            bool ok = true;
            for (Py_ssize_t i = 0; i < ti->children_size; i++) {
                type_info* info = ti->children[i];
                PyObject* got_item = PyDict_GetItem(
                    obj,
                    info->ob
                );

                if (!got_item) {
                    if ((intptr_t) info->df != -1) {
                        if (info->df) {
                            got_item = info->df;
                            if (PyCallable_Check(got_item)) {
                                got_item = PyObject_CallNoArgs(got_item); // its a factory
                                if (!got_item) {
                                    PyErr_Print();
                                    Py_DECREF(kwargs);
                                    Py_DECREF(obj);
                                    ok = false;
                                    break;
                                }
                            }
                        } else {
                            ok = false;
                            Py_DECREF(kwargs);
                            Py_DECREF(obj);
                            break;
                        }
                    } else {
                        continue;
                    }
                }

                PyObject* parsed_item = cast_from_typecodes(
                    info->children,
                    info->children_size,
                    got_item,
                    json_parser,
                    allow_casting
                );

                if (!parsed_item) {
                    Py_DECREF(kwargs);
                    Py_DECREF(obj);
                    ok = false;
                    break;
                }

                if (PyDict_SetItem(
                    kwargs,
                    info->ob,
                    parsed_item
                    ) < 0) {
                    Py_DECREF(kwargs);
                    Py_DECREF(obj);
                    Py_DECREF(parsed_item);
                    return NULL;
                };
                Py_DECREF(parsed_item);
            };

            if (!ok) break;

            PyObject* caller;
            caller = PyObject_GetAttrString(
                ti->ob,
                "__view_construct__"
            );
            if (!caller) {
                PyErr_Clear();
                caller = ti->ob;
            }

            PyObject* built = PyObject_VectorcallDict(
                caller,
                NULL,
                0,
                kwargs
            );

            Py_DECREF(kwargs);
            if (!built) {
                PyErr_Print();
                return NULL;
            }

            return built;
        }
        case TYPECODE_LIST: {
            PyObject* list;
            if (Py_IS_TYPE(
                item,
                &PyList_Type
                )) {
                Py_INCREF(item);
                list = item;
            }
            else {
                list = PyObject_Vectorcall(
                    json_parser,
                    (PyObject*[]) { item },
                    1,
                    NULL
                );

                if (!list) {
                    PyErr_Clear();
                    break;
                }

                if (!Py_IS_TYPE(
                    list,
                    &PyList_Type
                    )) {
                    break;
                }
            }

            int res = verify_list_typecodes(
                ti->children,
                ti->children_size,
                list,
                json_parser
            );
            if (res == -1) {
                Py_DECREF(list);
                return NULL;
            }

            if (res == 1) {
                Py_DECREF(list);
                break;
            }

            return list;
        }
        case TYPECODE_CLASSTYPES:
        default: {
            fprintf(
                stderr,
                "got bad typecode in cast_from_typecodes: %d\n",
                ti->typecode
            );
            VIEW_FATAL("invalid typecode");
        }
        }
    }
    if ((CHECK(NULL_ALLOWED)) && (item == NULL || item ==
                                  Py_None)) Py_RETURN_NONE;
    if (CHECK(STRING_ALLOWED)) {
        if (!PyObject_IsInstance(
            item,
            (PyObject*) &PyUnicode_Type
            ))
            return NULL;
        return Py_NewRef(item);
    }
    return NULL;
}

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


type_info** build_type_codes(PyObject* type_codes, Py_ssize_t len) {
    type_info** tps = calloc(
        sizeof(type_info),
        len
    );

    for (Py_ssize_t i = 0; i < len; i++) {
        PyObject* info = PyList_GetItem(
            type_codes,
            i
        );
        type_info* ti = malloc(sizeof(type_info));

        if (!info && ti) {
            for (int x = 0; x < i; x++)
                free_type_info(tps[x]);

            free(tps);
            if (ti) free(ti);
            return NULL;
        }

        PyObject* type_code = PyTuple_GetItem(
            info,
            0
        );
        PyObject* obj = PyTuple_GetItem(
            info,
            1
        );
        PyObject* children = PyTuple_GetItem(
            info,
            2
        );

        PyObject* df = PyTuple_GetItem(
            info,
            3
        );

        if (df) {
            if (PyObject_HasAttrString(
                df,
                "__VIEW_NODEFAULT__"
                )) df = NULL;
            else if (PyObject_HasAttrString(
                df,
                "__VIEW_NOREQ__"
                     ))
                df = (PyObject*) -1;
        }

        if (!type_code || !obj || !children) {
            for (int x = 0; x < i; x++)
                free_type_info(tps[x]);

            free(tps);
            return NULL;
        }

        if (!df) PyErr_Clear();

        Py_ssize_t code = PyLong_AsLong(type_code);

        Py_XINCREF(obj);
        ti->ob = obj;
        ti->typecode = code;
        // we cant use Py_XINCREF or Py_XDECREF because it could be -1
        if ((intptr_t) df > 0) Py_INCREF(df);
        ti->df = df;

        Py_ssize_t children_len = PySequence_Size(children);
        if (children_len == -1) {
            for (int x = 0; x < i; x++)
                free_type_info(tps[x]);

            free(tps);
            Py_XDECREF(obj);
            if ((intptr_t) df > 0) Py_DECREF(df);
            return NULL;
        }

        ti->children_size = children_len;
        type_info** children_info = build_type_codes(
            children,
            children_len
        );

        if (!children_info) {
            for (int x = 0; x < i; i++)
                free_type_info(tps[x]);

            free(tps);
            Py_XDECREF(obj);
            if ((intptr_t) df) Py_DECREF(df);
            return NULL;
        }

        ti->children = children_info;
        tps[i] = ti;
    }

    return tps;
}


int load_typecodes(
    route* r,
    PyObject* target
) {
    PyObject* iter = PyObject_GetIter(target);
    PyObject* item;
    Py_ssize_t index = 0;

    Py_ssize_t len = PySequence_Size(target);
    if (len == -1) {
        return -1;
    }

    r->inputs = PyMem_Calloc(
        len,
        sizeof(route_input*)
    );
    if (!r->inputs) return -1;

    while ((item = PyIter_Next(iter))) {
        route_input* inp = PyMem_Malloc(sizeof(route_input));
        r->inputs[index++] = inp;

        if (!inp) {
            Py_DECREF(iter);
            return -1;
        }

        if (Py_IS_TYPE(
            item,
            &PyLong_Type
            )) {
            int data = PyLong_AsLong(item);

            if (PyErr_Occurred()) {
                Py_DECREF(iter);
                return -1;
            }

            inp->route_data = data;
            continue;
        } else {
            inp->route_data = 0;
        }

        PyObject* is_body = Py_XNewRef(
            PyDict_GetItemString(
                item,
                "is_body"
            )
        );

        if (!is_body) {
            Py_DECREF(iter);
            PyMem_Free(r->inputs);
            return bad_input("is_body");
        }
        inp->is_body = PyObject_IsTrue(is_body);
        Py_DECREF(is_body);

        PyObject* name = Py_XNewRef(
            PyDict_GetItemString(
                item,
                "name"
            )
        );

        if (!name) {
            Py_DECREF(iter);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("name");
        }

        const char* cname = PyUnicode_AsUTF8(name);
        if (!cname) {
            Py_DECREF(iter);
            Py_DECREF(name);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return -1;
        }
        inp->name = strdup(cname);

        Py_DECREF(name);

        PyObject* has_default = PyDict_GetItemString(
            item,
            "has_default"
        );
        if (!has_default) {
            Py_DECREF(iter);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("has_default");
        }

        if (PyObject_IsTrue(has_default)) {
            inp->df = Py_XNewRef(
                PyDict_GetItemString(
                    item,
                    "default"
                )
            );
            if (!inp->df) {
                Py_DECREF(iter);
                PyMem_Free(r->inputs);
                PyMem_Free(inp);
                return bad_input("default");
            }
        } else {
            inp->df = NULL;
        }

        Py_DECREF(has_default);

        PyObject* codes = PyDict_GetItemString(
            item,
            "type_codes"
        );

        if (!codes) {
            Py_DECREF(iter);
            Py_XDECREF(inp->df);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("type_codes");
        }

        Py_ssize_t len = PySequence_Size(codes);
        if (len == -1) {
            Py_DECREF(iter);
            Py_XDECREF(inp->df);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return -1;
        }
        inp->types_size = len;
        if (!len) inp->types = NULL;
        else {
            inp->types = build_type_codes(
                codes,
                len
            );
            if (!inp->types) {
                Py_DECREF(iter);
                Py_XDECREF(inp->df);
                PyMem_Free(r->inputs);
                PyMem_Free(inp);
                return -1;
            }
        }

        PyObject* validators = PyDict_GetItemString(
            item,
            "validators"
        );

        if (!validators) {
            Py_DECREF(iter);
            Py_XDECREF(inp->df);
            free_type_codes(
                inp->types,
                inp->types_size
            );
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("validators");
        }

        Py_ssize_t size = PySequence_Size(validators);
        inp->validators = PyMem_Calloc(
            size,
            sizeof(PyObject*)
        );
        inp->validators_size = size;

        if (!inp->validators) {
            Py_DECREF(iter);
            free_type_codes(
                inp->types,
                inp->types_size
            );
            Py_XDECREF(inp->df);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return -1;
        }

        for (int i = 0; i < size; i++) {
            inp->validators[i] = Py_NewRef(
                PySequence_GetItem(
                    validators,
                    i
                )
            );
        }
    };

    Py_DECREF(iter);
    if (PyErr_Occurred()) return -1;
    return 0;
}


bool figure_has_body(PyObject* inputs) {
    PyObject* iter = PyObject_GetIter(inputs);
    PyObject* item;
    bool res = false;

    if (!iter) {
        return false;
    }

    while ((item = PyIter_Next(iter))) {
        if (Py_IS_TYPE(
            item,
            &PyLong_Type
            ))
            continue;
        PyObject* is_body = PyDict_GetItemString(
            item,
            "is_body"
        );

        if (!is_body) {
            Py_DECREF(iter);
            return false;
        }

        if (PyObject_IsTrue(is_body)) {
            res = true;
        }
        Py_DECREF(is_body);
    }

    Py_DECREF(iter);

    if (PyErr_Occurred()) {
        return false;
    }

    return res;
}