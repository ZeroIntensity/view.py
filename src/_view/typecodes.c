/*
 * view.py typecode implementation
 *
 * Typecodes are a view.py invention. In short, they are a fast
 * way to do runtime type checking.
 *
 * The simplest way to do runtime type checking would just
 * be to take a type, and run isinstance() (or in this case, PyObject_IsInstance).
 *
 * You could cheat a little by using something like Py_IS_TYPE to avoid the call,
 * but that's still not great. There's also no good way to do unions, generics,
 * or other typing shenanigans.
 *
 * Typecodes are view.py's solution. It starts in the _build_type_codes function,
 * which is in Python (since it's a one time cost, we don't have to worry about performance there).
 *
 * See _loader.py for the _build_type_codes implementation - in short, it takes
 * a type (including things like `typing._GenericAlias`, for generics), and converts
 * it into a list that the C API loader can understand.
 *
 * We'll stay away from the internals of that here - let's just focus on
 * the C implementation.
 *
 * A type code is stored in a type_info structure.
 * Technically speaking, the actual "type code" is just an integer on the structure,
 * and the whole structure is called "type information." However, view.py calls
 * type information typecodes for convenience and historical purposes.
 *
 * In most cases, you'll see type information being passed as an array, instead of
 * a single structure. An array of type information just means unions - a single type
 * is represented by *one* type_info structure, and then unions are just a bunch
 * of those chained together. We'll refer to a single structure as "type information,"
 * and an array of them as "typecodes."
 *
 * A typecode (or really, type_info structure) has three parts:
 *
 * - An 8-bit integer indicating the type. This is the actual "type code."
 * - An array of type information (typecodes) acting as the "children." This will be empty in many cases.
 *   This is generally for generic types. For example, if the type was `list[str]`, then the overall
 *   type code integer would be for lists, and then the children would contain the typecodes of the
 *   generics, which in this case would be that of `str`.
 * - A default value to use in case the value was missing when checked.
 *
 * The basic types are:
 * - Any (which if this exists anywhere on the typecode, the rest of it is skipped).
 * - String
 * - Integer
 * - Boolean
 * - Float
 * - None/null
 *
 * These types don't have any children, and are simply checked with CheckExact.
 *
 * view.py does what it can to cast the object to the given type at runtime. For example, if
 * the object was the string `"1"`, but the typecode is for an `int`, then it will
 * cast it (unless casting was disabled, which only happens when using the public typecode API).

 * If a string is anywhere on the typecode, then it means that every value can
 * be assigned to it. However, casting on strings is done lazily. So, if the typecode is
 * for `str | int`, then it will only try and cast it to a string if casting to an integer fails.
 *
 * The types that can have children are:
 *
 * - Dictionary/JSON
 * - List/array
 * - Classes
 *
 * Dictionaries and lists both use the children as generics, so if the typecode was
 * for a list, then it would expect all of it's items to be compliant with the
 * children typecodes.
 *
 * Note that dictionaries can only have string keys, so the children only apply
 * to the values.
 *
 * Classes are a bit special, since the only children they can have are of `TYPECODE_CLASSTYPES`.
 * `TYPECODE_CLASSTYPES` are only supported here, and must not be used anywhere else.
 *
 * A `TYPECODE_CLASSTYPES` represents an attribute of an object.
 * The children are the type of the attribute, and the default is stored like any other typecode.
 *
 * However, the name is stored in a sneaky way - there's actually a fourth field on the
 * type_info structure, which contains an extra Python object. This slot is only
 * present with a `TYPECODE_CLASSTYPES`, and contains a Python string containing
 * the name of the attribute.
 *
 * The only thing that can be casted to a class is a dictionary or a string that represents JSON.
 */
#include <Python.h>
#include <stdbool.h> // bool

#include <view/backport.h>
#include <view/inputs.h> // route_input
#include <view/results.h> // pymem_strdup
#include <view/route.h> // route
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
#define TC_VERIFY(typeobj)   \
        if (typeobj(         \
    value                    \
            )) {             \
            verified = true; \
        }                    \
        break;

/* Deallocator for type info */
static void
free_type_info(type_info *ti)
{
    Py_XDECREF(ti->ob);
    if ((intptr_t) ti->df > 0) Py_DECREF(ti->df);
    for (int i = 0; i < ti->children_size; i++)
    {
        free_type_info(ti->children[i]);
    }
}

/* Deallocator for an array of type information. */
void
free_type_codes(type_info **codes, Py_ssize_t len)
{
    for (Py_ssize_t i = 0; i < len; i++)
        free_type_info(codes[i]);
}

/*
 * Utility function for raising an error when the loader
 * passes some wrong input. This is semantically
 * similar to PyErr_BadASGI()
 *
 * In a perfect world, this will never be called.
 */
COLD static inline int
bad_input(const char *name)
{
    PyErr_Format(
        PyExc_SystemError,
        "missing key in loader dict: %s",
        name
    );
    return -1;
}

/*
 * Verify a dictionary object given typecodes.
 * This will update the dictionary with casted values.
 */
static int
verify_dict_typecodes(
    type_info **codes,
    Py_ssize_t len,
    PyObject *dict,
    PyObject *json_parser
)
{
    Py_ssize_t pos = 0;
    PyObject *key;
    PyObject *value;

    while (PyDict_Next(dict, &pos, &key, &value))
    {
        PyObject *casted_value = cast_from_typecodes(
            codes,
            len,
            value,
            json_parser,
            true
        );
        if (!casted_value) return -1;

        if (
            PyDict_SetItem(
                dict,
                key,
                casted_value
            ) < 0
        )
            return -1;
    }

    if (PyErr_Occurred())
        return -1;

    return 0;
}

/*
 * Verify a list with the given typecodes.
 * This will cast items in the list.
 */
static int
verify_list_typecodes(
    type_info **codes,
    Py_ssize_t len,
    PyObject *list,
    PyObject *json_parser
)
{
    Py_ssize_t list_len = PySequence_Size(list);
    if (list_len == -1) return -1;
    if (list_len == 0) return 0;

    for (int i = 0; i < list_len; i++)
    {
        PyObject *item = PyList_GET_ITEM(
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

        // This is intentional, do not make this -1
        if (!item) return 1;
        if (
            PyList_SetItem(
                list,
                i,
                item
            ) < 0
        )
        {
            Py_DECREF(item);
            return -1;
        }
    }

    return 0;
}

/*
 * Cast an object using the given typecodes.
 * This is essentially the "main" function of typecodes.
 *
 * The allow_casting parameter is whether to allow an object to not
 * be the actual type. For example, if casting is enabled, the string `"1"` can
 * be casted to the integer `1`, if the typecode supports it. If this is disabled,
 * then it will ensure that the `item` parameter is directly an instance of the type.
 */
PyObject *
cast_from_typecodes(
    type_info **codes,
    Py_ssize_t len,
    PyObject *item,
    PyObject *json_parser,
    bool allow_casting
)
{
    if (!codes)
    {
        // type is Any
        if (!item) Py_RETURN_NONE;
        return item;
    }
    ;

    typecode_flag typecode_flags = 0;

    for (Py_ssize_t i = 0; i < len; i++)
    {
        if (PyErr_Occurred())
            break;

        type_info *ti = codes[i];

        switch (ti->typecode)
        {
        case TYPECODE_ANY:
        {
            return item;
        }
        case TYPECODE_STR:
        {
            if (!allow_casting)
            {
                if (PyUnicode_CheckExact(item))
                {
                    return Py_NewRef(item);
                }
                PyErr_SetString(
                    PyExc_ValueError,
                    "Got non-string without casting enabled"
                );
                return NULL;
            }
            typecode_flags |= STRING_ALLOWED;
            break;
        }
        case TYPECODE_NONE:
        {
            if (!allow_casting)
            {
                if (item == Py_None)
                {
                    return Py_NewRef(item);
                }
                PyErr_SetString(
                    PyExc_ValueError,
                    "Got non-None without casting enabled"
                );
                return NULL;
            }
            typecode_flags |= NULL_ALLOWED;
            break;
        }
        case TYPECODE_INT:
        {
            if (
                PyLong_CheckExact(
                    item
                )
            )
            {
                return Py_NewRef(item);
            } else if (!allow_casting)
            {
                PyErr_SetString(
                    PyExc_ValueError,
                    "Got non-int without casting enabled"
                );
                return NULL;
            }

            PyObject *py_int = PyLong_FromUnicodeObject(
                item,
                10
            );
            if (!py_int)
            {
                break;
            }
            return py_int;
        }
        case TYPECODE_BOOL:
        {
            if (
                PyBool_Check(
                    item
                )
            ) return Py_NewRef(item);
            else if (!allow_casting)
            {
                PyErr_SetString(
                    PyExc_ValueError,
                    "Got non-bool without casting enabled"
                );
                return NULL;
            } else if (PyLong_CheckExact(item))
            {
                long val = PyLong_AsLong(item);
                if (val == -1 && PyErr_Occurred())
                    return NULL;
                return PyBool_FromLong(val);
            } else if (PyUnicode_CheckExact(item))
            {
                const char *str = PyUnicode_AsUTF8(item);
                PyObject *py_bool = NULL;
                if (!str)
                    return NULL;
                if (
                    strcmp(
                        str,
                        "true"
                    ) == 0
                )
                {
                    py_bool = Py_NewRef(Py_True);
                } else if (
                    strcmp(
                        str,
                        "false"
                    ) == 0
                )
                {
                    py_bool = Py_NewRef(Py_False);
                }

                if (py_bool != NULL)
                    return py_bool;
            }
            PyErr_Format(PyExc_ValueError, "Not bool-like: %R", item);
            break;
        }
        case TYPECODE_FLOAT:
        {
            if (
                PyFloat_CheckExact(
                    item
                )
            ) return Py_NewRef(item);
            else if (!allow_casting)
            {
                PyErr_SetString(
                    PyExc_ValueError,
                    "Got non-float without casting enabled"
                );
                return NULL;
            }
            PyObject *flt = PyFloat_FromString(item);
            if (!flt)
            {
                break;
            }
            return flt;
        }
        case TYPECODE_DICT:
        {
            PyObject *obj;
            if (
                PyDict_Check(
                    item
                )
            )
            {
                obj = Py_NewRef(item);
            } else if (!allow_casting)
            {
                PyErr_SetString(
                    PyExc_ValueError,
                    "Got non-dict without casting enabled"
                );
                return NULL;
            } else
            {
                obj = PyObject_Vectorcall(
                    json_parser,
                    (PyObject *[]) { item },
                    1,
                    NULL
                );
            }
            if (!obj)
            {
                break;
            }
            int res = verify_dict_typecodes(
                ti->children,
                ti->children_size,
                obj,
                json_parser
            );
            if (res == -1)
            {
                Py_DECREF(obj);
                return NULL;
            }

            if (res == 1)
            {
                Py_DECREF(obj);
                break;
            }

            return obj;
        }
        case TYPECODE_CLASS:
        {
            if (!allow_casting)
            {
                if (
                    !Py_IS_TYPE(
                        item,
                        Py_TYPE(ti->ob)
                    )
                )
                {
                    PyErr_Format(
                        PyExc_ValueError,
                        "Got non-%R instance without casting enabled",
                        Py_TYPE(ti->ob)
                    );
                    return NULL;
                }

                return Py_NewRef(item);
            }
            PyObject *kwargs = PyDict_New();
            if (!kwargs)
                return NULL;
            PyObject *obj;
            if (
                PyDict_CheckExact(item) || Py_IS_TYPE(
                    item,
                    Py_TYPE(ti->ob)
                )
            )
            {
                obj = Py_NewRef(item);
            } else
            {
                obj = PyObject_Vectorcall(
                    json_parser,
                    (PyObject *[]) { item },
                    1,
                    NULL
                );
            }

            if (!obj)
            {
                Py_DECREF(kwargs);
                break;
            }

            bool ok = true;
            for (Py_ssize_t i = 0; i < ti->children_size; i++)
            {
                type_info *info = ti->children[i];
                PyObject *got_item = PyDict_GetItem(
                    obj,
                    info->ob
                );

                if (!got_item)
                {
                    if ((intptr_t) info->df != -1)
                    {
                        if (info->df)
                        {
                            got_item = info->df;
                            if (PyCallable_Check(got_item))
                            {
                                got_item = PyObject_CallNoArgs(got_item); // It's a factory
                                if (!got_item)
                                {
                                    Py_DECREF(kwargs);
                                    Py_DECREF(obj);
                                    ok = false;
                                    break;
                                }
                            }
                        } else
                        {
                            PyErr_Format(
                                PyExc_ValueError,
                                "Missing key: %S",
                                info->ob
                            );
                            ok = false;
                            Py_DECREF(kwargs);
                            Py_DECREF(obj);
                            break;
                        }
                    } else
                    {
                        continue;
                    }
                }

                PyObject *parsed_item = cast_from_typecodes(
                    info->children,
                    info->children_size,
                    got_item,
                    json_parser,
                    allow_casting
                );

                if (!parsed_item)
                {
                    Py_DECREF(kwargs);
                    Py_DECREF(obj);
                    ok = false;
                    break;
                }

                if (
                    PyDict_SetItem(
                        kwargs,
                        info->ob,
                        parsed_item
                    ) < 0
                )
                {
                    Py_DECREF(kwargs);
                    Py_DECREF(obj);
                    Py_DECREF(parsed_item);
                    return NULL;
                }
                Py_DECREF(parsed_item);
            }

            if (!ok) break;

            PyObject *caller;
            caller = PyObject_GetAttrString(
                ti->ob,
                "__view_construct__"
            );
            if (!caller)
            {
                PyErr_Clear();
                caller = ti->ob;
            }

            PyObject *built = PyObject_VectorcallDict(
                caller,
                NULL,
                0,
                kwargs
            );

            Py_DECREF(kwargs);
            if (!built)
            {
                return NULL;
            }

            return built;
        }
        case TYPECODE_LIST:
        {
            PyObject *list;
            if (
                Py_IS_TYPE(
                    item,
                    &PyList_Type
                )
            )
            {
                Py_INCREF(item);
                list = item;
            } else
            {
                list = PyObject_Vectorcall(
                    json_parser,
                    (PyObject *[]) { item },
                    1,
                    NULL
                );

                if (!list)
                {
                    break;
                }

                if (
                    !Py_IS_TYPE(
                        list,
                        &PyList_Type
                    )
                )
                {
                    PyErr_Format(
                        PyExc_TypeError,
                        "Expected array, got %R",
                        list
                    );
                    break;
                }
            }

            int res = verify_list_typecodes(
                ti->children,
                ti->children_size,
                list,
                json_parser
            );
            if (res == -1)
            {
                Py_DECREF(list);
                return NULL;
            }

            if (res == 1)
            {
                Py_DECREF(list);
                break;
            }

            return list;
        }
        case TYPECODE_CLASSTYPES:
        default:
        {
            fprintf(
                stderr,
                "got bad typecode in cast_from_typecodes: %d\n",
                ti->typecode
            );
            VIEW_FATAL("invalid typecode");
        }
        }
    }
    PyObject *final_err = PyErr_GetRaisedException();

    if (
        (CHECK(NULL_ALLOWED)) &&
        (item == NULL || item ==
         Py_None)
    )
    {
        Py_XDECREF(final_err);
        Py_RETURN_NONE;
    }
    if (CHECK(STRING_ALLOWED))
    {
        if (
            !PyObject_IsInstance(
                item,
                (PyObject *) &PyUnicode_Type
            )
        )
        {
            if (!final_err)
                PyErr_SetString(
                    PyExc_ValueError,
                    "Expected string"
                );
            else
                PyErr_SetRaisedException(final_err);
            return NULL;
        }

        Py_XDECREF(final_err);
        return Py_NewRef(item);
    }

    assert(final_err != NULL);
    PyErr_SetRaisedException(final_err);
    return NULL;
}

/*
 * Convert Python typecodes generated by the loader into C typecodes.
 *
 * This is essentially the bridge for typecodes between C and Python.
 */
type_info **
build_type_codes(PyObject *type_codes, Py_ssize_t len)
{
    type_info **tps = PyMem_Calloc(
        sizeof(type_info),
        len
    );

    for (Py_ssize_t i = 0; i < len; i++)
    {
        PyObject *info = PyList_GetItem(
            type_codes,
            i
        );
        type_info *ti = PyMem_Malloc(sizeof(type_info));

        if (!info && ti)
        {
            for (int x = 0; x < i; x++)
                free_type_info(tps[x]);

            PyMem_Free(tps);
            if (ti) PyMem_Free(ti);
            return NULL;
        }

        PyObject *type_code = PyTuple_GetItem(
            info,
            0
        );
        PyObject *obj = PyTuple_GetItem(
            info,
            1
        );
        PyObject *children = PyTuple_GetItem(
            info,
            2
        );

        PyObject *df = PyTuple_GetItem(
            info,
            3
        );

        if (df)
        {
            if (
                PyObject_HasAttrString(
                    df,
                    "__VIEW_NODEFAULT__"
                )
            ) df = NULL;
            else if (
                PyObject_HasAttrString(
                    df,
                    "__VIEW_NOREQ__"
                )
            )
                df = (PyObject *) -1;
        }

        if (!type_code || !obj || !children)
        {
            for (int x = 0; x < i; x++)
                free_type_info(tps[x]);

            PyMem_Free(tps);
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
        if (children_len == -1)
        {
            for (int x = 0; x < i; x++)
                free_type_info(tps[x]);

            PyMem_Free(tps);
            Py_XDECREF(obj);
            if ((intptr_t) df > 0) Py_DECREF(df);
            return NULL;
        }

        ti->children_size = children_len;
        type_info **children_info = build_type_codes(
            children,
            children_len
        );

        if (!children_info)
        {
            for (int x = 0; x < i; i++)
                free_type_info(tps[x]);

            PyMem_Free(tps);
            Py_XDECREF(obj);
            if ((intptr_t) df) Py_DECREF(df);
            return NULL;
        }

        ti->children = children_info;
        tps[i] = ti;
    }

    return tps;
}

int
load_typecodes(
    route *r,
    PyObject *target
)
{
    PyObject *iter = PyObject_GetIter(target);
    PyObject *item;
    Py_ssize_t index = 0;

    Py_ssize_t len = PySequence_Size(target);
    if (len == -1)
    {
        return -1;
    }

    r->inputs = PyMem_Calloc(
        len,
        sizeof(route_input *)
    );
    if (!r->inputs) return -1;

    while ((item = PyIter_Next(iter)))
    {
        route_input *inp = PyMem_Malloc(sizeof(route_input));
        r->inputs[index++] = inp;

        if (!inp)
        {
            Py_DECREF(iter);
            return -1;
        }

        if (
            Py_IS_TYPE(
                item,
                &PyLong_Type
            )
        )
        {
            int data = PyLong_AsLong(item);

            if (PyErr_Occurred())
            {
                Py_DECREF(iter);
                return -1;
            }

            inp->route_data = data;
            continue;
        } else
        {
            inp->route_data = 0;
        }

        PyObject *is_body = Py_XNewRef(
            PyDict_GetItemString(
                item,
                "is_body"
            )
        );

        if (!is_body)
        {
            Py_DECREF(iter);
            PyMem_Free(r->inputs);
            return bad_input("is_body");
        }
        inp->is_body = PyObject_IsTrue(is_body);
        Py_DECREF(is_body);

        PyObject *name = Py_XNewRef(
            PyDict_GetItemString(
                item,
                "name"
            )
        );

        if (!name)
        {
            Py_DECREF(iter);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("name");
        }

        Py_ssize_t name_size;
        const char *cname = PyUnicode_AsUTF8AndSize(name, &name_size);
        if (!cname)
        {
            Py_DECREF(iter);
            Py_DECREF(name);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return -1;
        }
        inp->name = pymem_strdup(cname, name_size);

        Py_DECREF(name);

        PyObject *has_default = PyDict_GetItemString(
            item,
            "has_default"
        );
        if (!has_default)
        {
            Py_DECREF(iter);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("has_default");
        }

        if (PyObject_IsTrue(has_default))
        {
            inp->df = Py_XNewRef(
                PyDict_GetItemString(
                    item,
                    "default"
                )
            );
            if (!inp->df)
            {
                Py_DECREF(iter);
                PyMem_Free(r->inputs);
                PyMem_Free(inp);
                return bad_input("default");
            }
        } else
        {
            inp->df = NULL;
        }

        Py_DECREF(has_default);

        PyObject *codes = PyDict_GetItemString(
            item,
            "type_codes"
        );

        if (!codes)
        {
            Py_DECREF(iter);
            Py_XDECREF(inp->df);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("type_codes");
        }

        Py_ssize_t len = PySequence_Size(codes);
        if (len == -1)
        {
            Py_DECREF(iter);
            Py_XDECREF(inp->df);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return -1;
        }
        inp->types_size = len;
        if (!len) inp->types = NULL;
        else
        {
            inp->types = build_type_codes(
                codes,
                len
            );
            if (!inp->types)
            {
                Py_DECREF(iter);
                Py_XDECREF(inp->df);
                PyMem_Free(r->inputs);
                PyMem_Free(inp);
                return -1;
            }
        }

        PyObject *validators = PyDict_GetItemString(
            item,
            "validators"
        );

        if (!validators)
        {
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
            sizeof(PyObject *)
        );
        inp->validators_size = size;

        if (!inp->validators)
        {
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

        for (int i = 0; i < size; i++)
        {
            inp->validators[i] = Py_NewRef(
                PySequence_GetItem(
                    validators,
                    i
                )
            );
        }
    }
    ;

    Py_DECREF(iter);
    if (PyErr_Occurred()) return -1;
    return 0;
}

/*
 * Figure out whether there's a body input in the list of route inputs.
 *
 * This is for optimization - if a route doesn't have a body input,
 * then receiving and parsing the body can be skipped at runtime.
 */
bool
figure_has_body(PyObject *inputs)
{
    PyObject *iter = PyObject_GetIter(inputs);
    PyObject *item;
    bool res = false;

    if (!iter)
    {
        return false;
    }

    while ((item = PyIter_Next(iter)))
    {
        if (
            Py_IS_TYPE(
                item,
                &PyLong_Type
            )
        )
            continue;
        PyObject *is_body = PyDict_GetItemString(
            item,
            "is_body"
        );

        if (!is_body)
        {
            Py_DECREF(iter);
            return false;
        }

        if (PyObject_IsTrue(is_body))
        {
            res = true;
        }
        Py_DECREF(is_body);
    }

    Py_DECREF(iter);

    if (PyErr_Occurred())
    {
        return false;
    }

    return res;
}

/*
 * TCPublic is just the base type for the Python wrapper.
 * Breaking changes are allowed on the API.
 */

typedef struct
{
    PyObject_HEAD
    type_info **codes;
    Py_ssize_t codes_len;
    PyObject *json_parser;
} TCPublic;

/* Deallocator for a public type validation object. */
static void
dealloc(TCPublic *self)
{
    free_type_codes(
        self->codes,
        self->codes_len
    );
    Py_DECREF(self->json_parser);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

/*
 * Allocator function for the TCPublic object.
 * This is considered private - breaking changes are allowed.
 */
static PyObject *
new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    TCPublic *self = (TCPublic *) type->tp_alloc(
        type,
        0
    );
    if (!self)
        return NULL;

    return (PyObject *) self;
}

/*
 * Python wrapper around cast_from_typecodes()
 * Also considered private - breaking changes are possible.
 *
 * This is known as _cast() in Python
 */
static PyObject *
cast_from_typecodes_public(PyObject *self, PyObject *args)
{
    TCPublic *tc = (TCPublic *) self;
    PyObject *obj;
    int allow_cast;

    if (
        !PyArg_ParseTuple(
            args,
            "Op",
            &obj,
            &allow_cast
        )
    )
        return NULL;

    PyObject *res = cast_from_typecodes(
        tc->codes,
        tc->codes_len,
        obj,
        tc->json_parser,
        allow_cast
    );
    if (!res)
    {
        return NULL;
    }

    return res;
}

/*
 * Load Python typecodes into the object as C type codes.
 */
static PyObject *
compile(PyObject *self, PyObject *args)
{
    TCPublic *tc = (TCPublic *) self;
    PyObject *list;
    PyObject *json_parser;

    if (
        !PyArg_ParseTuple(
            args,
            "OO",
            &list,
            &json_parser
        )
    )
        return NULL;

    if (!PySequence_Check(list))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "expected a sequence"
        );
        return NULL;
    }

    Py_ssize_t size = PySequence_Size(list);
    if (size < 0)
        return NULL;

    type_info **info = build_type_codes(
        list,
        size
    );
    tc->codes = info;
    tc->codes_len = size;
    tc->json_parser = Py_NewRef(json_parser);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] =
{
    {"_compile", (PyCFunction) compile, METH_VARARGS, NULL},
    {"_cast", (PyCFunction) cast_from_typecodes_public, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};


PyTypeObject TCPublicType =
{
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
