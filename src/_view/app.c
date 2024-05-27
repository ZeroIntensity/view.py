#include <Python.h>

#include <stdbool.h>
#include <signal.h>

#include <view/app.h>
#include <view/awaitable.h>
#include <view/backport.h>
#include <view/errors.h>
#include <view/parsers.h> // handle_route_query
#include <view/parts.h> // extract_parts, load_parts
#include <view/routing.h> // route_free, route_new, handle_route
#include <view/map.h>
#include <view/view.h> // VIEW_FATAL

#define LOAD_ROUTE(target) \
    char* path; \
    PyObject* callable; \
    PyObject* inputs; \
    Py_ssize_t cache_rate; \
    PyObject* errors; \
    PyObject* parts = NULL; \
    if (!PyArg_ParseTuple( \
        args, \
        "zOnOOO", \
        &path, \
        &callable, \
        &cache_rate, \
        &inputs, \
        &errors, \
        &parts \
        )) return NULL; \
    route* r = route_new( \
        callable, \
        PySequence_Size(inputs), \
        cache_rate, \
        figure_has_body(inputs) \
    ); \
    if (!r) return NULL; \
    if (load_typecodes( \
        r, \
        inputs \
        ) < 0) { \
        route_free(r); \
        return NULL; \
    } \
    if (load_errors(r, errors) < 0) { \
        route_free(r); \
        return NULL; \
    } \
    if (!map_get(self->all_routes, path)) { \
        int* num = malloc(sizeof(int)); \
        if (!num) { \
            PyErr_NoMemory(); \
            route_free(r); \
            return NULL; \
        } \
        *num = 1; \
        map_set(self->all_routes, path, num);\
    } \
    if (!PySequence_Size(parts)) \
        map_set(self-> target, path, r); \
    else \
        if (load_parts(self, self-> target, parts, r) < 0) return NULL;

#define ROUTE(target) static PyObject* target ( \
    ViewApp* self, \
    PyObject* args \
) { \
        LOAD_ROUTE(target); \
        Py_RETURN_NONE; \
}

int PyErr_BadASGI(void) {
    PyErr_SetString(
        PyExc_RuntimeError,
        "problem with view.py's ASGI server (this is a bug!)"
    );
    return -1;
}

<<<<<<< HEAD
// port of strsep for use on windows
char* v_strsep(char** stringp, const char* delim) {
    char* rv = *stringp;
    if (rv) {
        *stringp += strcspn(
            *stringp,
            delim
        );
        if (**stringp)
            *(*stringp)++ = '\0';
        else
            *stringp = 0;
    }
    return rv;
}

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

route* route_new(
    PyObject* callable,
    Py_ssize_t inputs_size,
    Py_ssize_t cache_rate,
    bool has_body
) {
    route* r = malloc(sizeof(route));
    if (!r) return (route*) PyErr_NoMemory();

    r->cache = NULL;
    r->callable = Py_NewRef(callable);
    r->cache_rate = cache_rate;
    r->cache_index = 0;
    r->cache_headers = NULL;
    r->cache_status = 0;
    r->inputs = NULL;
    r->inputs_size = inputs_size;
    r->has_body = has_body;
    r->is_http = true;

    // transports
    r->routes = NULL;
    r->r = NULL;

    for (int i = 0; i < 28; i++)
        r->client_errors[i] = NULL;

    for (int i = 0; i < 11; i++)
        r->server_errors[i] = NULL;

    return r;
}


void route_free(route* r) {
    for (int i = 0; i < r->inputs_size; i++) {
        if (r->inputs[i]->route_data) {
            continue;
        }
        Py_XDECREF(r->inputs[i]->df);
        free_type_codes(
            r->inputs[i]->types,
            r->inputs[i]->types_size
        );

        for (int i = 0; i < r->inputs[i]->validators_size; i++) {
            Py_DECREF(r->inputs[i]->validators[i]);
        }
    }

    PyMem_Free(r->inputs);

    for (int i = 0; i < r->middleware_size; i++)
        Py_DECREF(r->middleware[i]);

    PyMem_Free(r->middleware);
    Py_XDECREF(r->cache_headers);
    Py_DECREF(r->callable);

    for (int i = 0; i < 11; i++)
        Py_XDECREF(r->server_errors[i]);

    for (int i = 0; i < 28; i++)
        Py_XDECREF(r->client_errors[i]);

    if (r->cache) free(r->cache);
    free(r);
}

void route_input_print(route_input* ri) {
    puts("route_input {");
    printf(
        "name: %s\n",
        ri->name
    );
    printf("df: ");
    PyObject_Print(
        ri->df,
        stdout,
        Py_PRINT_RAW
    );
    puts("");
    printf(
        "is_body: %d\n",
        ri->is_body
    );

    puts("validators [");
    for (int i = 0; i < ri->validators_size; i++) {
        PyObject* o = ri->validators[i];
        PyObject_Print(
            o,
            stdout,
            Py_PRINT_RAW
        );
        puts("");
    }
    puts("]");

    puts("}");
}

void route_print(route* r) {
    puts("route {");
    printf("callable: ");
    PyObject_Print(
        r->callable,
        stdout,
        Py_PRINT_RAW
    );
    puts("");
    printf("route_inputs [");
    for (int i = 0; i < r->inputs_size; i++) {
        route_input* ri = r->inputs[i];
        route_input_print(ri);
    }
    puts("]");
    printf(
        "cache: %s\ncache_headers: ",
        r->cache ? r->cache : "\"\""
    );
    PyObject_Print(
        r->cache_headers,
        stdout,
        Py_PRINT_RAW
    );
    printf(
        "\ncache_status: %d\ncache_index: %ld\ncache_rate: %ld\n",
        r->cache_status,
        r->cache_index,
        r->cache_rate
    );

    if (r->r) {
        printf("r: ");
        route_print(r->r);
        puts("");
    } else {
        puts("r: NULL");
    }

    if (r->routes) {
        printf("routes: ");
        print_map(
            r->routes,
            (map_print_func) route_print
        );
        puts("");
    } else {
        puts("routes: NULL");
    }

    puts("}");
}

route* route_transport_new(route* r) {
    route* rt = malloc(sizeof(route));
    if (!rt) return (route*) PyErr_NoMemory();
    rt->cache = NULL;
    rt->callable = NULL;
    rt->cache_rate = 0;
    rt->cache_index = 0;
    rt->cache_headers = NULL;
    rt->cache_status = 0;
    rt->inputs = NULL;
    rt->inputs_size = 0;
    rt->has_body = false;
    rt->is_http = false;

    for (int i = 0; i < 28; i++)
        rt->client_errors[i] = NULL;

    for (int i = 0; i < 11; i++)
        rt->server_errors[i] = NULL;

    rt->routes = NULL;
    rt->r = r;
    return rt;
}

static PyObject* query_parser(
    app_parsers* parsers,
    const char* data
) {
    PyObject* py_str = PyUnicode_FromString(data);

    if (!py_str)
        return NULL;

    PyObject* obj = PyObject_Vectorcall(
        parsers->query,
        (PyObject*[]) { py_str },
        1,
        NULL
    );

    Py_DECREF(py_str);
    return obj; // no need for null check
}

#define TC_VERIFY(typeobj) if (typeobj( \
                    value \
                    )) { \
                    verified = true; \
                } break;


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

static PyObject* build_data_input(
    int num,
    PyObject* scope,
    PyObject* receive,
    PyObject* send
) {
    switch (num) {
    case 1: return context_from_data(scope);
    case 2: return ws_from_data(
        scope,
        send,
        receive
    );

    default:
        VIEW_FATAL("got invalid route data number");
    }
    return NULL; // to make editor happy
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

static PyObject** generate_params(
    app_parsers* parsers,
    const char* data,
    PyObject* query,
    route_input** inputs,
    Py_ssize_t inputs_size,
    PyObject* scope,
    PyObject* receive,
    PyObject* send
) {
    PyObject* py_str = PyUnicode_FromString(data);
    if (!py_str)
        return NULL;

    PyObject* obj = PyObject_Vectorcall(
        parsers->json,
        (PyObject*[]) { py_str },
        1,
        NULL
    );
    Py_DECREF(py_str);

    if (!obj)
        return NULL;

    PyObject** ob = calloc(
        inputs_size,
        sizeof(PyObject*)
    );

    if (!ob) {
        Py_DECREF(obj);
        return NULL;
    }

    for (int i = 0; i < inputs_size; i++) {
        route_input* inp = inputs[i];
        if (inp->route_data) {
            PyObject* data = build_data_input(
                inp->route_data,
                scope,
                receive,
                send
            );
            if (!data) {
                Py_DECREF(obj);
                free(ob);
                return NULL;
            }

            ob[i] = data;
            continue;
        }

        PyObject* raw_item = PyDict_GetItemString(
            inp->is_body ? obj : query,
            inp->name
        );
        PyObject* item = cast_from_typecodes(
            inp->types,
            inp->types_size,
            raw_item,
            parsers->json,
            true
        );

        if (!item) {
            Py_DECREF(obj);
            free(ob);
            return NULL;
        }

        for (int x = 0; x < inp->validators_size; x++) {
            PyObject* o = PyObject_Vectorcall(
                inp->validators[x],
                (PyObject*[]) { item },
                1,
                NULL
            );
            if (!PyObject_IsTrue(o)) {
                Py_DECREF(o);
                free(ob);
                Py_DECREF(obj);
                Py_DECREF(item);
                return NULL;
            }
        }

        ob[i] = item;
    }

    return ob;
}

=======
>>>>>>> 2732cf7344a5c028353852ec0c019f1525467a76
static PyObject* new(PyTypeObject* tp, PyObject* args, PyObject* kwds) {
    ViewApp* self = (ViewApp*) tp->tp_alloc(
        tp,
        0
    );
    if (!self) return NULL;
    self->startup = NULL;
    self->cleanup = NULL;
    self->get = map_new(
        4,
        (map_free_func) route_free
    );
    self->put = map_new(
        4,
        (map_free_func) route_free
    );
    self->post = map_new(
        4,
        (map_free_func) route_free
    );
    self->delete = map_new(
        4,
        (map_free_func) route_free
    );
    self->patch = map_new(
        4,
        (map_free_func) route_free
    );
    self->options = map_new(
        4,
        (map_free_func) route_free
    );
    self->websocket = map_new(
        4,
        (map_free_func) route_free
    );
    self->all_routes = map_new(
        4,
        free
    );

    if (!self->options || !self->patch || !self->delete ||
        !self->post ||
        !self->put || !self->put || !self->get) {
        return NULL;
    };

    for (int i = 0; i < 28; i++)
        self->client_errors[i] = NULL;

    for (int i = 0; i < 11; i++)
        self->server_errors[i] = NULL;

    self->has_path_params = false;

    return (PyObject*) self;
}

static int init(PyObject* self, PyObject* args, PyObject* kwds) {
    PyErr_SetString(
        PyExc_TypeError,
        "ViewApp is not constructable"
    );
    return -1;
}

static int lifespan(PyObject* awaitable, PyObject* result) {
    ViewApp* self;
    PyObject* send;
    PyObject* receive;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        NULL,
        &receive,
        &send
        ) < 0)
        return -1;

    PyObject* tp = PyDict_GetItemString(
        result,
        "type"
    );
    const char* type = PyUnicode_AsUTF8(tp);
    Py_DECREF(tp);

    bool is_startup = !strcmp(
        type,
        "lifespan.startup"
    );
    PyObject* target_obj = is_startup ? self->startup : self->cleanup;
    if (target_obj) {
        if (!PyObject_CallNoArgs(target_obj))
            return -1;
    }

    PyObject* send_dict = Py_BuildValue(
        "{s:s}",
        "type",
        is_startup ? "lifespan.startup.complete" :
        "lifespan.shutdown.complete"
    );

    if (!send_dict)
        return -1;

    PyObject* send_coro = PyObject_Vectorcall(
        send,
        (PyObject*[]) { send_dict },
        1,
        NULL
    );

    if (!send_coro)
        return -1;

    Py_DECREF(send_dict);

    if (PyAwaitable_AWAIT(
        awaitable,
        send_coro
        ) < 0) {
        Py_DECREF(send_coro);
        return -1;
    }
    Py_DECREF(send_coro);
    if (!is_startup) return 0;

    PyObject* aw = PyAwaitable_New();
    if (!aw)
        return -1;

    PyObject* recv_coro = PyObject_CallNoArgs(receive);
    if (!recv_coro) {
        Py_DECREF(aw);
        return -1;
    }

    if (PyAwaitable_AddAwait(
        aw,
        recv_coro,
        lifespan,
        NULL
        ) < 0) {
        Py_DECREF(aw);
        Py_DECREF(recv_coro);
        return -1;
    };

    return 0;
}

static void dealloc(ViewApp* self) {
    Py_XDECREF(self->cleanup);
    Py_XDECREF(self->startup);
    map_free(self->get);
    map_free(self->post);
    map_free(self->put);
    map_free(self->patch);
    map_free(self->delete);
    map_free(self->options);
    map_free(self->websocket);
    Py_XDECREF(self->exceptions);

    for (int i = 0; i < 11; i++)
        Py_XDECREF(self->server_errors[i]);

    for (int i = 0; i < 28; i++)
        Py_XDECREF(self->client_errors[i]);

    Py_XDECREF(self->error_type);
    Py_TYPE(self)->tp_free(self);
}

static const char* dict_get_str(PyObject* dict, const char* str) {
    Py_INCREF(dict);
    PyObject* ob = PyDict_GetItemString(
        dict,
        str
    );
    Py_DECREF(dict);
    if (!ob) {
        PyErr_BadASGI();
        return NULL;
    }

    const char* result = PyUnicode_AsUTF8(ob);
    return result;
}

static PyObject* app(
    ViewApp* self,
    PyObject* const* args,
    Py_ssize_t nargs
) {
    assert(nargs == 3);
    PyObject* scope = args[0];
    PyObject* receive = args[1];
    PyObject* send = args[2];

    PyObject* tp = PyDict_GetItemString(
        scope,
        "type"
    );

    if (!tp) {
        PyErr_BadASGI();
        return NULL;
    }

    const char* type = PyUnicode_AsUTF8(tp);
    Py_DECREF(tp);

    PyObject* awaitable = PyAwaitable_New();
    if (!awaitable)
        return NULL;

    if (!strcmp(
        type,
        "lifespan"
        )) {
        PyObject* recv_coro = PyObject_CallNoArgs(receive);
        if (!recv_coro) {
            Py_DECREF(awaitable);
            return NULL;
        }

        if (PyAwaitable_SaveValues(
            awaitable,
            4,
            self,
            scope,
            receive,
            send
        ) < 0) {
            Py_DECREF(awaitable);
            return NULL;
        }

        if (PyAwaitable_AddAwait(
            awaitable,
            recv_coro,
            lifespan,
            NULL
            ) < 0) {
            Py_DECREF(awaitable);
            Py_DECREF(recv_coro);
            return NULL;
        };
        Py_DECREF(recv_coro);
        return awaitable;
    }

    PyObject* raw_path_obj = PyDict_GetItemString(
        scope,
        "path"
    );
    if (!raw_path_obj) {
        Py_DECREF(awaitable);
        PyErr_BadASGI();
        return NULL;
    }
    const char* raw_path = PyUnicode_AsUTF8(raw_path_obj);
    if (!raw_path) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyAwaitable_SaveValues(
        awaitable,
        5,
        self,
        scope,
        receive,
        send,
        raw_path_obj
        ) < 0) {
        Py_DECREF(awaitable);
        return NULL;
    }

    bool is_http = !strcmp(
        type,
        "http"
    );

    size_t len = strlen(raw_path);
    char* path;
    if (raw_path[len - 1] == '/' && len != 1) {
        path = malloc(len);
        if (!path) {
            Py_DECREF(awaitable);
            return PyErr_NoMemory();
        }

        for (size_t i = 0; i < len - 1; i++)
            path[i] = raw_path[i];

        path[len - 1] = '\0';
    } else {
        path = strdup(raw_path);
        if (!path) {
            Py_DECREF(awaitable);
            return PyErr_NoMemory();
        }
    }
    const char* method = NULL;

    if (is_http) {
        method = dict_get_str(
            scope,
            "method"
        );
    }

    PyObject* query_obj = PyDict_GetItemString(
        scope,
        "query_string"
    );

    if (!query_obj) {
        Py_DECREF(awaitable);
        free(path);
        return NULL;
    }

    const char* query_str = PyBytes_AsString(query_obj);

    if (!query_str) {
        Py_DECREF(awaitable);
        free(path);
        return NULL;
    }
    char* query = strdup(query_str);
    map* ptr = self->websocket; // ws by default
    const char* method_str;

    if (is_http) {
        if (!strcmp(
            method,
            "GET"
            )) {
            ptr = self->get;
            method_str = "GET";
        }
        else if (!strcmp(
            method,
            "POST"
                 )) {
            ptr = self->post;
            method_str = "POST";
        }
        else if (!strcmp(
            method,
            "PATCH"
                 )) {
            ptr = self->patch;
            method_str = "PATCH";
        }
        else if (!strcmp(
            method,
            "PUT"
                 )) {
            ptr = self->put;
            method_str = "PUT";
        }
        else if (!strcmp(
            method,
            "DELETE"
                 )) {
            ptr = self->delete;
            method_str = "DELETE";
        }
        else if (!strcmp(
            method,
            "OPTIONS"
                 )) {
            ptr = self->options;
            method_str = "OPTIONS";
        }
        if (!ptr) {
            ptr = self->get;
        }
    }

    route* r = map_get(
        ptr,
        path
    );
    PyObject** params = NULL;
    Py_ssize_t* size = NULL;

    if (!r || r->r) {
        if (!self->has_path_params) {
            if (map_get(
                self->all_routes,
                path
                )) {
                if (fire_error(
                    self,
                    awaitable,
                    405,
                    NULL,
                    NULL,
                    NULL,
                    method_str
                    ) < 0) {
                    Py_DECREF(awaitable);
                    free(path);
                    return NULL;
                }
                free(path);
                return awaitable;
            }
            if (fire_error(
                self,
                awaitable,
                404,
                NULL,
                NULL,
                NULL,
                method_str
                ) < 0) {
                Py_DECREF(awaitable);
                free(path);
                return NULL;
            }
            free(path);
            return awaitable;
        }

        // path parameter extraction
        int res = extract_parts(
            self,
            awaitable,
            ptr,
            path,
            method_str,
            size,
            &r,
            &params
        );
        if (res < 0) {
            free(path);
            free(size);

            if (res == -1) {
                // -1 denotes that an exception occurred, raise it
                Py_DECREF(awaitable);
                return NULL;
            }

            // -2 denotes that an error can be sent to the client, return
            // the awaitable for execution of send()
            return awaitable;
        }
    }

    if (is_http && (r->cache_rate != -1) && (r->cache_index++ <
                                             r->cache_rate) &&
        r->cache) {
        PyObject* dct = Py_BuildValue(
            "{s:s,s:i,s:O}",
            "type",
            "http.response.start",
            "status",
            r->cache_status,
            "headers",
            r->cache_headers
        );

        if (!dct) {
            if (size) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                free(params);
                free(size);
            }
            free(path);
            Py_DECREF(awaitable);
            return NULL;
        }

        PyObject* coro = PyObject_Vectorcall(
            send,
            (PyObject*[]) { dct },
            1,
            NULL
        );

        Py_DECREF(dct);

        if (!coro) {
            if (size) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                free(params);
                free(size);
            }
            free(path);
            Py_DECREF(awaitable);
            return NULL;
        }

        if (PyAwaitable_AWAIT(
            awaitable,
            coro
            ) < 0) {
            if (size) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                free(params);
                free(size);
            }
            Py_DECREF(awaitable);
            Py_DECREF(coro);
            free(path);
            return NULL;
        };

        Py_DECREF(coro);

        PyObject* dc = Py_BuildValue(
            "{s:s,s:y}",
            "type",
            "http.response.body",
            "body",
            r->cache
        );

        if (!dc) {
            if (size) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                free(params);
                free(size);
            }
            Py_DECREF(awaitable);
            free(path);
            return NULL;
        }

        coro = PyObject_Vectorcall(
            send,
            (PyObject*[]) { dc },
            1,
            NULL
        );

        Py_DECREF(dc);

        if (!coro) {
            if (size) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                free(params);
                free(size);
            }
            Py_DECREF(awaitable);
            free(path);
            return NULL;
        }

        if (PyAwaitable_AWAIT(
            awaitable,
            coro
            ) < 0) {
            if (size) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                free(params);
                free(size);
            }
            Py_DECREF(awaitable);
            Py_DECREF(coro);
            free(path);
            return NULL;
        }

        Py_DECREF(coro);
        free(path);
        return awaitable;
    }

    if (PyAwaitable_SaveArbValues(
        awaitable,
        4,
        r,
        params,
        size,
        method_str
        ) < 0) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (r->inputs_size != 0) {
        if (!r->has_body) {
            if (handle_route_query(
                awaitable,
                query
                ) < 0) {
                Py_DECREF(awaitable);
                free(path);
                return NULL;
            };

            return awaitable;
        }

        if (handle_route(
            awaitable,
            query
            ) < 0) {
            Py_DECREF(awaitable);
            return NULL;
        };

        return awaitable;
    } else {
        if (!is_http) VIEW_FATAL("got a websocket without an input!");

        PyObject* res_coro;
        if (size) {
            res_coro = PyObject_Vectorcall(
                r->callable,
                params,
                *size,
                NULL
            );

            for (int i = 0; i < *size; i++)
                Py_DECREF(params[i]);

            free(path);
            free(params);
            free(size);
        } else res_coro = PyObject_CallNoArgs(r->callable);

        if (!res_coro) {
            Py_DECREF(awaitable);
            free(path);
            return NULL;
        }

        if (!res_coro) {
            if (server_err(
                self,
                awaitable,
                500,
                r,
                NULL,
                method_str
                ) < 0)
                return NULL;
            return awaitable;
        }
        if (PyAwaitable_AddAwait(
            awaitable,
            res_coro,
            handle_route_callback,
            route_error
            ) < 0) {
            Py_DECREF(res_coro);
            free(path);
            Py_DECREF(awaitable);
            return NULL;
        }
    }

    return awaitable;
}

ROUTE(get);
ROUTE(post);
ROUTE(patch);
ROUTE(put);
ROUTE(delete);
ROUTE(options);

static PyObject* websocket(ViewApp* self, PyObject* args) {
    LOAD_ROUTE(websocket);
    r->is_http = false;
    Py_RETURN_NONE;
}

static PyObject* err_handler(ViewApp* self, PyObject* args) {
    PyObject* handler;
    int status_code;

    if (!PyArg_ParseTuple(
        args,
        "iO",
        &status_code,
        &handler
        )) return NULL;

    if (status_code < 400 || status_code > 511) {
        PyErr_Format(
            PyExc_ValueError,
            "%d is not a valid status code",
            status_code
        );
        return NULL;
    }

    if (status_code >= 500) {
        self->server_errors[status_code - 500] = Py_NewRef(handler);
    } else {
        uint16_t index = hash_client_error(status_code);
        if (index == 600) {
            PyErr_Format(
                PyExc_ValueError,
                "%d is not a valid status code",
                status_code
            );
            return NULL;
        }
        self->client_errors[index] = Py_NewRef(handler);
    }

    Py_RETURN_NONE;
}

static PyObject* exc_handler(ViewApp* self, PyObject* args) {
    PyObject* dict;
    if (!PyArg_ParseTuple(
        args,
        "O!",
        &PyDict_Type,
        &dict
        )) return NULL;
    if (self->exceptions) {
        PyDict_Merge(
            self->exceptions,
            dict,
            1
        );
    } else {
        self->exceptions = Py_NewRef(dict);
    }

    Py_RETURN_NONE;
}

static void sigsegv_handler(int signum) {
    signal(
        SIGSEGV,
        SIG_DFL
    );
    VIEW_FATAL("segmentation fault");
}

static PyObject* set_dev_state(ViewApp* self, PyObject* args) {
    int value;
    if (!PyArg_ParseTuple(
        args,
        "p",
        &value
        )) return NULL;
    self->dev = (bool) value;

    if (value)
        signal(
            SIGSEGV,
            sigsegv_handler
        );

    Py_RETURN_NONE;
}

static PyObject* supply_parsers(ViewApp* self, PyObject* args) {
    PyObject* query;
    PyObject* json;

    if (!PyArg_ParseTuple(
        args,
        "OO",
        &query,
        &json
        ))
        return NULL;

    self->parsers.query = query;
    self->parsers.json = json;
    Py_RETURN_NONE;
}

static PyObject* register_error(ViewApp* self, PyObject* args) {
    PyObject* type;

    if (!PyArg_ParseTuple(
        args,
        "O",
        &type
        ))
        return NULL;

    if (Py_TYPE(type) != &PyType_Type) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "_register_error got an object that is not a type"
        );
        return NULL;
    }

    self->error_type = Py_NewRef(type);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"asgi_app_entry", (PyCFunction) app, METH_FASTCALL, NULL},
    {"_get", (PyCFunction) get, METH_VARARGS, NULL},
    {"_post", (PyCFunction) post, METH_VARARGS, NULL},
    {"_put", (PyCFunction) put, METH_VARARGS, NULL},
    {"_patch", (PyCFunction) patch, METH_VARARGS, NULL},
    {"_delete", (PyCFunction) delete, METH_VARARGS, NULL},
    {"_options", (PyCFunction) options, METH_VARARGS, NULL},
    {"_websocket", (PyCFunction) websocket, METH_VARARGS, NULL},
    {"_set_dev_state", (PyCFunction) set_dev_state, METH_VARARGS, NULL},
    {"_err", (PyCFunction) err_handler, METH_VARARGS, NULL},
    {"_supply_parsers", (PyCFunction) supply_parsers, METH_VARARGS, NULL},
    {"_register_error", (PyCFunction) register_error, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

PyTypeObject ViewAppType = {
    PyVarObject_HEAD_INIT(
        NULL,
        0
    )
    .tp_name = "_view.ViewApp",
    .tp_basicsize = sizeof(ViewApp),
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_init = (initproc) init,
    .tp_methods = methods,
    .tp_new = new,
    .tp_dealloc = (destructor) dealloc
};
