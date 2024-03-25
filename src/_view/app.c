#include <Python.h>
#include <view/view.h>
#include <stdbool.h>
#include <stdint.h>
#include <signal.h>

#define ER(code, str) case code: return str
#define LOAD_ROUTE(target) \
    char* path; \
    PyObject* callable; \
    PyObject* inputs; \
    Py_ssize_t cache_rate; \
    PyObject* errors; \
    PyObject* parts = NULL; \
    PyObject* middleware_list; \
    if (!PyArg_ParseTuple( \
        args, \
        "zOnOOOO", \
        &path, \
        &callable, \
        &cache_rate, \
        &inputs, \
        &errors, \
        &parts, \
        &middleware_list \
        )) return NULL; \
    route* r = route_new( \
        callable, \
        PySequence_Size(inputs), \
        cache_rate, \
        figure_has_body(inputs) \
    ); \
    if (!r) return NULL; \
    if (load( \
        r, \
        inputs \
        ) < 0) { \
        route_free(r); \
        return NULL; \
    } \
    if (load_middleware(r, middleware_list) < 0) { \
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
#define TRANSPORT_MAP() map_new(2, (map_free_func) route_free)

#define ROUTE(target) static PyObject* target ( \
    ViewApp* self, \
    PyObject* args \
) { \
        LOAD_ROUTE(target); \
        Py_RETURN_NONE; \
}
#define ERR(code, msg) case code: return send_raw_text( \
    awaitable, \
    send, \
    code, \
    msg \
    );
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

typedef struct _route_input route_input;
typedef struct _app_parsers app_parsers;
typedef PyObject** (* parserfunc)(app_parsers*, const char*, PyObject*,
                                  route_input**, Py_ssize_t);

typedef struct _app_parsers {
    PyObject* query;
    PyObject* json;
} app_parsers;

typedef struct _ViewApp {
    PyObject ob_base; // PyObject_HEAD doesn't work on windows for some reason
    PyObject* startup;
    PyObject* cleanup;
    map* get;
    map* post;
    map* put;
    map* patch;
    map* delete;
    map* options;
    map* websocket;
    map* all_routes;
    PyObject* client_errors[28];
    PyObject* server_errors[11];
    bool dev;
    PyObject* exceptions;
    app_parsers parsers;
    bool has_path_params;
    PyObject* error_type;
} ViewApp;

struct _type_info {
    uint8_t typecode;
    PyObject* ob;
    type_info** children;
    Py_ssize_t children_size;
    PyObject* df;
};

typedef struct _route_input {
    int route_data; // if this is above 0, assume all other items are undefined
    type_info** types;
    Py_ssize_t types_size;
    PyObject* df;
    PyObject** validators;
    Py_ssize_t validators_size;
    char* name;
    bool is_body;
} route_input;

typedef struct Route route;

struct Route {
    PyObject* callable;
    char* cache;
    PyObject* cache_headers;
    uint16_t cache_status;
    Py_ssize_t cache_index;
    Py_ssize_t cache_rate;
    route_input** inputs;
    Py_ssize_t inputs_size;
    PyObject* client_errors[28];
    PyObject* server_errors[11];
    PyObject* exceptions;
    bool has_body;
    bool is_http;
    PyObject** middleware;
    Py_ssize_t middleware_size;
    PyObject* raw_path;

    // transport attributes
    map* routes;
    route* r;
};

/*
 * -- routes and r information --
 * lets say the requested route is GET /app/12345/index and 12345 is a path parameter.
 * we would first map_get(app->get, "/app"). if this returns NULL, it is a 404.
 * then, we map_get(route->routes, "/12345"). if NULL, we check if a route->r is available.
 * if so, this is a path parameter, we save the value and move on to the next. otherwise, 404.
 * we repeat this process until we reach the end of the URL. so, next we do map_get(route->r->routes, "/index").
 * */

typedef enum {
    STRING_ALLOWED = 1 << 0,
    NULL_ALLOWED = 2 << 0
} typecode_flag;

int PyErr_BadASGI(void) {
    PyErr_SetString(
        PyExc_RuntimeError,
        "problem with view.py's ASGI server (this is a bug!)"
    );
    return -1;
}

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

static int send_raw_text(
    PyObject* awaitable,
    PyObject* send,
    int status,
    const char* res_str,
    PyObject* headers     /* may be NULL */
) {
    PyObject* coro;
    PyObject* send_dict;
    if (!headers) {
        send_dict = Py_BuildValue(
            "{s:s,s:i,s:[[y,y]]}",
            "type",
            "http.response.start",
            "status",
            status,
            "headers",
            "content-type",
            "text/plain"
        );

        if (!send_dict)
            return -1;

        coro = PyObject_Vectorcall(
            send,
            (PyObject*[]) { send_dict },
            1,
            NULL
        );
    } else {
        send_dict = Py_BuildValue(
            "{s:s,s:i,s:O}",
            "type",
            "http.response.start",
            "status",
            status,
            "headers",
            headers
        );

        if (!send_dict)
            return -1;

        coro = PyObject_Vectorcall(
            send,
            (PyObject*[]) { send_dict },
            1,
            NULL
        );
    }
    Py_DECREF(send_dict);
    if (!coro)
        return -1;

    if (PyAwaitable_AWAIT(
        awaitable,
        coro
        ) < 0) {
        Py_DECREF(coro);
        return -1;
    };

    Py_DECREF(coro);
    PyObject* dict = Py_BuildValue(
        "{s:s,s:y}",
        "type",
        "http.response.body",
        "body",
        res_str
    );

    if (!dict)
        return -1;


    coro = PyObject_Vectorcall(
        send,
        (PyObject*[]) { dict },
        1,
        NULL
    );

    Py_DECREF(dict);

    if (!coro)
        return -1;

    if (PyAwaitable_AWAIT(
        awaitable,
        coro
        ) < 0) {
        Py_DECREF(coro);
        return -1;
    }

    Py_DECREF(coro);
    return 0;
}

/*
   400 - 0
   401 - 1
   402 - 2
   403 - 3
   404 - 4
   405 - 5
   406 - 6
   407 - 7
   408 - 8
   409 - 9
   410 - 10
   411 - 11
   412 - 12
   413 - 13
   414 - 14
   415 - 15
   416 - 16
   417 - 17
   418 - 18
   NOTICE: status codes start to skip around now!
   421 - 19
   422 - 20
   423 - 21
   424 - 22
   425 - 23
   426 - 24
   428 - 25
   429 - 26
   431 - 27
   451 - 28
 */

static uint16_t hash_client_error(int status) {
    if (status < 419) {
        return status - 400;
    }

    if (status < 427) {
        return status - 402;
    }

    if (status < 430) {
        return status - 406;
    }

    if (status == 431) {
        return 27;
    }

    if (status == 451) {
        return 28;
    }

    PyErr_Format(
        invalid_status_error,
        "%d is not a valid status code",
        status
    );
    return 600;
}

static inline uint16_t hash_server_error(int status) {
    uint16_t index = status - (status < 509 ? 500 : 501);
    if ((index < 0) || (index > 10)) {
        PyErr_Format(
            invalid_status_error,
            "%d is not a valid status code",
            status
        );
        return 600;
    }
    return index;
}

static const char* get_err_str(int status) {
    switch (status) {
    ER(
        400,
        "Bad Request"
    );
    ER(
        401,
        "Unauthorized"
    );
    ER(
        402,
        "Payment Required"
    );
    ER(
        403,
        "Forbidden"
    );
    ER(
        404,
        "Not Found"
    );
    ER(
        405,
        "Method Not Allowed"
    );
    ER(
        406,
        "Not Acceptable"
    );
    ER(
        407,
        "Proxy Authentication Required"
    );
    ER(
        408,
        "Request Timeout"
    );
    ER(
        409,
        "Conflict"
    );
    ER(
        410,
        "Gone"
    );
    ER(
        411,
        "Length Required"
    );
    ER(
        412,
        "Precondition Failed"
    );
    ER(
        413,
        "Payload Too Large"
    );
    ER(
        414,
        "URI Too Long"
    );
    ER(
        415,
        "Unsupported Media Type"
    );
    ER(
        416,
        "Range Not Satisfiable"
    );
    ER(
        417,
        "Expectation Failed"
    );
    ER(
        418,
        "I'm a teapot"
    );
    ER(
        421,
        "Misdirected Request"
    );
    ER(
        422,
        "Unprocessable Content"
    );
    ER(
        423,
        "Locked"
    );
    ER(
        424,
        "Failed Dependency"
    );
    ER(
        425,
        "Too Early"
    );
    ER(
        426,
        "Upgrade Required"
    );
    ER(
        428,
        "Precondition Required"
    );
    ER(
        429,
        "Too Many Requests"
    );
    ER(
        431,
        "Request Header Fields Too Large"
    );
    ER(
        451,
        "Unavailable for Legal Reasons"
    );
    ER(
        500,
        "Internal Server Error"
    );
    ER(
        501,
        "Not Implemented"
    );
    ER(
        502,
        "Bad Gateway"
    );
    ER(
        503,
        "Service Unavailable"
    );
    ER(
        504,
        "Gateway Timeout"
    );
    ER(
        505,
        "HTTP Version Not Supported"
    );
    ER(
        506,
        "Variant Also Negotiates"
    );
    ER(
        507,
        "Insufficent Storage"
    );
    ER(
        508,
        "Loop Detected"
    );
    ER(
        510,
        "Not Extended"
    );
    ER(
        511,
        "Network Authentication Required"
    );
    }

    PyErr_Format(
        invalid_status_error,
        "invalid status code: %d",
        status
    );
    return NULL;
}


static int find_result_for(
    PyObject* target,
    char** res_str,
    int* status,
    PyObject* headers
) {
    if (Py_IS_TYPE(
        target,
        &PyUnicode_Type
        )) {
        const char* tmp = PyUnicode_AsUTF8(target);
        if (!tmp) return -1;
        *res_str = strdup(tmp);
    } else if (Py_IS_TYPE(
        target,
        &PyDict_Type
               )) {
        PyObject* item;
        PyObject* v;
        Py_ssize_t pos = 0;

        while (PyDict_Next(
            target,
            &pos,
            &item,
            &v
               )) {
            const char* v_str = PyUnicode_AsUTF8(v);
            if (!v_str) {
                return -1;
            }

            PyObject* item_bytes = PyUnicode_EncodeLocale(
                item,
                "strict"
            );

            if (!item_bytes) {
                return -1;
            }

            PyObject* header_list = PyTuple_New(2);

            if (!header_list) {
                Py_DECREF(item_bytes);
                return -1;
            }

            if (PyTuple_SetItem(
                header_list,
                0,
                item_bytes
                ) < 0) {
                Py_DECREF(header_list);
                Py_DECREF(item_bytes);
                return -1;
            };

            Py_DECREF(item_bytes);

            PyObject* v_bytes = PyBytes_FromString(v_str);

            if (!v_bytes) {
                Py_DECREF(header_list);
                return -1;
            }

            if (PyTuple_SetItem(
                header_list,
                1,
                v_bytes
                ) < 0) {
                Py_DECREF(header_list);
                return -1;
            };

            Py_DECREF(v_bytes);

            if (PyList_Append(
                headers,
                header_list
                ) < 0) {
                Py_DECREF(header_list);
                return -1;
            }
            Py_DECREF(header_list);
        }

        if (PyErr_Occurred()) return -1;
    } else if (Py_IS_TYPE(
        target,
        &PyLong_Type
               )) {
        *status = (int) PyLong_AsLong(target);
    } else if (Py_IS_TYPE(
        target,
        &PyTuple_Type
               )) {

        for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(target); i++) {
            PyObject* t_value = PyTuple_GET_ITEM(
                target,
                i
            );
            if (!PyTuple_Check(
                t_value
                )) {
                PyErr_SetString(
                    PyExc_TypeError,
                    "raw header tuple should contain tuples"
                );
                return -1;
            }

            PyList_Append(
                headers,
                t_value
            );
        }

        if (PyErr_Occurred()) {
            return -1;
        }
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "returned tuple should only contain a str, int, or dict"
        );
        return -1;
    }

    return 0;
}

static int handle_result_impl(
    PyObject* raw_result,
    char** res_target,
    int* status_target,
    PyObject** headers_target
) {
    char* res_str = NULL;
    int status = 200;
    PyObject* headers = PyList_New(0);
    PyObject* result;

    PyObject* view_result = PyObject_GetAttrString(
        raw_result,
        "__view_result__"
    );
    PyErr_Clear();

    if (view_result) {
        result = PyObject_CallNoArgs(view_result);
        if (!result)
            return -1;
    } else result = raw_result;

    if (PyUnicode_CheckExact(
        result
        )) {
        const char* tmp = PyUnicode_AsUTF8(result);
        if (!tmp) return -1;
        res_str = strdup(tmp);
    } else if (PyTuple_CheckExact(
        result
               )) {
        if (PySequence_Size(result) > 3) {
            PyErr_SetString(
                PyExc_TypeError,
                "returned tuple should not exceed 3 elements"
            );
            return -1;
        } else {
            PyObject* first = PyTuple_GetItem(
                result,
                0
            );
            PyObject* second = PyTuple_GetItem(
                result,
                1
            );
            PyObject* third = PyTuple_GetItem(
                result,
                2
            );

            PyErr_Clear();

            if (first && find_result_for(
                first,
                &res_str,
                &status,
                headers
                ) < 0) return -1;

            if (second && find_result_for(
                second,
                &res_str,
                &status,
                headers
                ) < 0) return -1;

            if (third && find_result_for(
                third,
                &res_str,
                &status,
                headers
                ) < 0) return -1;
        }
    } else {
        PyErr_Format(
            PyExc_TypeError,
            "%R is not a valid return value for route",
            result
        );
        return -1;
    }

    *res_target = res_str;
    *status_target = status;
    *headers_target = headers;
    return 0;
}

static int handle_result(
    PyObject* raw_result,
    char** res_target,
    int* status_target,
    PyObject** headers_target,
    PyObject* raw_path,
    const char* method
) {
    int res = handle_result_impl(
        raw_result,
        res_target,
        status_target,
        headers_target
    );
    if (!route_log) return res;

    PyObject* args = Py_BuildValue(
        "(iOs)",
        *status_target,
        raw_path,
        method
    );

    if (!PyObject_Call(route_log, args, NULL)) {
        Py_DECREF(args);
        return -1;
    }
    Py_DECREF(args);

    return res;
}

static int finalize_err_cb(PyObject* awaitable, PyObject* result) {
    PyObject* send;
    PyObject* raw_path;
    const char* method_str;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &send,
        &raw_path
        ) < 0)
        return -1;

    if (PyAwaitable_UnpackArbValues(awaitable, NULL, &method_str) < 0)
        return -1;

    char* res_str;
    int status_code;
    PyObject* headers;

    if (handle_result(
        result,
        &res_str,
        &status_code,
        &headers,
        raw_path,
        method_str
        ) < 0) {
        Py_DECREF(result);
        return -1;
    }

    if (send_raw_text(
        awaitable,
        send,
        status_code,
        res_str,
        headers
        ) < 0) {
        Py_DECREF(result);
        free(res_str);
        return -1;
    }

    free(res_str);
    return 0;
}

static int run_err_cb(
    PyObject* awaitable,
    PyObject* handler,
    PyObject* send,
    int status,
    bool* called,
    const char* message,
    route* r,
    PyObject* raw_path
) {
    if (!handler) {
        if (called) *called = false;
        const char* msg;
        if (!message) {
            msg = get_err_str(status);
            if (!msg)
                return -1;
        } else msg = message;

        if (send_raw_text(
            awaitable,
            send,
            status,
            msg,
            NULL
            ) < 0
        ) {
            return -1;
        }

        return 0;
    }
    if (called) *called = true;

    PyObject* coro = PyObject_CallNoArgs(handler);

    if (!coro)
        return -1;

    PyObject* new_awaitable = PyAwaitable_New();

    if (!new_awaitable) {
        Py_DECREF(coro);
        return -1;
    }

    if (PyAwaitable_SaveValues(
        new_awaitable,
        2,
        send,
        raw_path
        ) < 0) {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    if (PyAwaitable_SaveArbValues(new_awaitable, 1, r) < 0) {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    if (PyAwaitable_AddAwait(
        new_awaitable,
        coro,
        finalize_err_cb,
        NULL
        ) < 0) {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    if (PyAwaitable_AWAIT(
        awaitable,
        new_awaitable
        ) < 0) {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    return 0;
}

static int fire_error(
    ViewApp* self,
    PyObject* awaitable,
    int status,
    route* r,
    bool* called,
    const char* message
) {
    PyObject* send;
    PyObject* raw_path;

    if (PyAwaitable_UnpackValues(
        awaitable,
        NULL,
        NULL,
        NULL,
        &send,
        &raw_path
        ) < 0)
        return -1;

    uint16_t index = 0;
    PyObject* handler = NULL;

    if (status >= 500) {
        index = hash_server_error(status);
        if (index == 600)
            return -1;
        if (r) handler = r->server_errors[index];
        if (!handler) handler = self->server_errors[index];
    } else {
        index = hash_client_error(status);
        if (index == 600)
            return -1;
        if (r) handler = r->client_errors[index];
        if (!handler) handler = self->client_errors[index];
    }

    if (run_err_cb(
        awaitable,
        handler,
        send,
        status,
        called,
        message,
        r,
        raw_path
        ) < 0) {
        if (send_raw_text(
            awaitable,
            send,
            500,
            "failed to dispatch error handler",
            NULL
            ) < 0) {
            return -1;
        }
    }

    return 0;
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
        &send,
        NULL
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

static int server_err_exc(
    ViewApp* self,
    PyObject* awaitable,
    uint16_t status,
    route* r,
    bool* handler_was_called,
    PyObject* msg
) {
    const char* message = NULL;
    PyObject* msg_str = NULL;

    if (self->dev) {
        msg_str = PyObject_Str(msg);
        if (!msg_str)
            return -1;

        message = PyUnicode_AsUTF8(msg_str);
        if (!message) {
            Py_DECREF(msg_str);
            return -1;
        }
    }

    if (fire_error(
        self,
        awaitable,
        status,
        r,
        handler_was_called,
        message
        ) < 0) {
        Py_XDECREF(msg_str);
        return -1;
    }

    //Py_XDECREF(msg_str);
    return 0;
}

static int server_err(
    ViewApp* self,
    PyObject* awaitable,
    uint16_t status,
    route* r,
    bool* handler_was_called
) {
    int res = server_err_exc(
        self,
        awaitable,
        status,
        r,
        handler_was_called,
        PyErr_Occurred()
    );
    PyErr_Clear();
    return res;
}

static int route_error(
    PyObject* awaitable,
    PyObject* tp,
    PyObject* value,
    PyObject* tb
) {
    ViewApp* self;
    route* r;
    PyObject* send;
    bool handler_was_called;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        NULL,
        NULL,
        &send,
        NULL
        ) < 0) return -1;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        NULL,
        NULL,
        NULL
        ) < 0) return -1;

    if (tp == self->error_type) {
        PyObject* status_obj = PyObject_GetAttrString(
            value,
            "status"
        );
        if (!status_obj)
            return -2;

        PyObject* msg_obj = PyObject_GetAttrString(
            value,
            "message"
        );

        if (!msg_obj) {
            Py_DECREF(status_obj);
            return -2;
        }

        int status = PyLong_AsLong(status_obj);
        if ((status == -1) && PyErr_Occurred()) {
            Py_DECREF(status_obj);
            Py_DECREF(msg_obj);
            return -2;
        }

        const char* message = NULL;

        if (msg_obj != Py_None) {
            message = PyUnicode_AsUTF8(msg_obj);
            if (!message) {
                Py_DECREF(status_obj);
                Py_DECREF(msg_obj);
                return -2;
            }
        }

        if (fire_error(
            self,
            awaitable,
            status,
            r,
            NULL,
            message
            ) < 0) {
            Py_DECREF(status_obj);
            Py_DECREF(msg_obj);
            return -2;
        }

        Py_DECREF(status_obj);
        Py_DECREF(msg_obj);
        return 0;
    }

    if (!r->is_http) {
        // send a websocket error code
        PyObject* send_dict;
        if (self->dev) {
            PyObject* str = PyObject_Str(value);
            if (!str)
                return -1;

            send_dict = Py_BuildValue(
                "{s:s,s:i,s:S}",
                "type",
                "websocket.close",
                "code",
                1006,
                "reason",
                str
            );
            Py_DECREF(str);
        } else send_dict = Py_BuildValue(
            "{s:s,s:i}",
            "type",
            "websocket.close",
            "code",
            1006
        );

        if (!send_dict)
            return -1;

        PyObject* coro = PyObject_Vectorcall(
            send,
            (PyObject*[]) { send_dict },
            1,
            NULL
        );
        Py_DECREF(send_dict);

        if (PyAwaitable_AWAIT(
            awaitable,
            coro
            ) < 0) {
            Py_DECREF(coro);
            return -1;
        }
        Py_DECREF(coro);

        return 0;
    }

    if (server_err_exc(
        self,
        awaitable,
        500,
        r,
        &handler_was_called,
        value
        ) < 0) {
        return -1;
    }

    if (!handler_was_called) {
        PyErr_Restore(
            tp,
            value,
            tb
        );
        PyErr_Print();
    }

    return 0;
}


static int handle_route_callback(
    PyObject* awaitable,
    PyObject* result
) {
    PyObject* send;
    PyObject* receive;
    PyObject* raw_path;
    route* r;
    const char* method_str;

    if (PyAwaitable_UnpackValues(
        awaitable,
        NULL,
        NULL,
        &receive,
        &send,
        &raw_path
        ) < 0) return -1;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        NULL,
        NULL,
        &method_str
        ) < 0) return -1;

    char* res_str;
    int status;
    PyObject* headers;

    if (handle_result(
        result,
        &res_str,
        &status,
        &headers,
        raw_path,
        method_str
        ) < 0) {
        return -1;
    }

    if (r->cache_rate > 0) {
        r->cache = res_str;
        r->cache_status = status;
        r->cache_headers = Py_NewRef(headers);
        r->cache_index = 0;
    }

    PyObject* dc = Py_BuildValue(
        "{s:s,s:i,s:O}",
        "type",
        "http.response.start",
        "status",
        status,
        "headers",
        headers
    );

    if (!dc)
        return -1;

    PyObject* coro = PyObject_Vectorcall(
        send,
        (PyObject*[]) { dc },
        1,
        NULL
    );

    Py_DECREF(dc);

    if (!coro)
        return -1;

    if (PyAwaitable_AWAIT(
        awaitable,
        coro
        ) < 0) {
        Py_DECREF(coro);
        return -1;
    };

    Py_DECREF(coro);
    PyObject* dct = Py_BuildValue(
        "{s:s,s:y}",
        "type",
        "http.response.body",
        "body",
        res_str
    );

    if (!dct)
        return -1;


    coro = PyObject_Vectorcall(
        send,
        (PyObject*[]) { dct },
        1,
        NULL
    );

    Py_DECREF(dct);
    if (r->cache_rate <= 0) free(res_str);
    if (!coro)
        return -1;

    if (PyAwaitable_AWAIT(
        awaitable,
        coro
        ) < 0) {
        Py_DECREF(coro);
        return -1;
    }

    Py_DECREF(coro);
    return 0;
}

static int handle_route_impl(
    PyObject* awaitable,
    char* body,
    char* query
) {
    route* r;
    ViewApp* self;
    Py_ssize_t* size;
    PyObject** path_params;
    PyObject* scope;
    PyObject* receive;
    PyObject* send;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        &scope,
        &receive,
        &send,
        NULL
        ) < 0) {
        return -1;
    }

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        &path_params,
        &size,
        NULL
        ) < 0) {
        return -1;
    }

    PyObject* query_obj = query_parser(
        &self->parsers,
        query
    );

    if (!query_obj) {
        PyErr_Clear();
        return server_err(
            self,
            awaitable,
            400,
            r,
            NULL
        );
    }

    PyObject** params = generate_params(
        &self->parsers,
        body,
        query_obj,
        r->inputs,
        r->inputs_size,
        scope,
        receive,
        send
    );

    Py_DECREF(query_obj);

    if (!params) {
        // parsing failed
        PyErr_Clear();

        return server_err(
            self,
            awaitable,
            400,
            r,
            NULL
        );
    }

    PyObject* coro;

    if (size) {
        PyObject** merged = calloc(
            r->inputs_size + (*size),
            sizeof(PyObject*)
        );

        for (int i = 0; i < (*size); i++)
            merged[i] = path_params[i];

        for (int i = *size; i < r->inputs_size + *size; i++)
            merged[i] = params[i];

        for (int i = 0; i < r->middleware_size; i++) {
            PyObject* res = PyObject_Vectorcall(
                r->middleware[i],
                merged,
                r->inputs_size + (*size),
                NULL
            );

            if (!res) {
                for (int x = 0; x < r->inputs_size + *size; x++)
                    Py_DECREF(merged[x]);

                free(path_params);
                free(size);
                free(merged);
                if (server_err(
                    self,
                    awaitable,
                    500,
                    r,
                    NULL
                    ) < 0)
                    return -1;
                return 0;
            }
        }

        coro = PyObject_Vectorcall(
            r->callable,
            merged,
            r->inputs_size + (*size),
            NULL
        );

        for (int i = 0; i < r->inputs_size + *size; i++)
            Py_DECREF(merged[i]);

        free(path_params);
        free(size);
        free(merged);
        if (server_err(
            self,
            awaitable,
            500,
            r,
            NULL
            ) < 0)
            return -1;
    } else {
        for (int i = 0; i < r->middleware_size; i++) {
            PyObject* res = PyObject_Vectorcall(
                r->middleware[i],
                params,
                r->inputs_size,
                NULL
            );

            if (!res) {
                for (int x = 0; x < r->inputs_size; x++)
                    Py_DECREF(params[x]);

                if (server_err(
                    self,
                    awaitable,
                    500,
                    r,
                    NULL
                    ) < 0)
                    return -1;
                return 0;
            }

            if (PyCoro_CheckExact(res)) {
                if (PyAwaitable_AddAwait(
                    awaitable,
                    res,
                    NULL,
                    route_error
                    ) <
                    0) {
                    if (server_err(
                        self,
                        awaitable,
                        500,
                        r,
                        NULL
                        ) < 0)
                        return -1;
                    return 0;
                }
            }
        }

        coro = PyObject_Vectorcall(
            r->callable,
            params,
            r->inputs_size,
            NULL
        );


        for (int i = 0; i < r->inputs_size; i++)
            Py_DECREF(params[i]);
    }

    if (!coro)
        return -1;

    if (!Py_IS_TYPE(
        coro,
        &PyCoro_Type
        )) {
        if (handle_route_callback(
            awaitable,
            coro
            ) < 0) {
            if (server_err(
                self,
                awaitable,
                500,
                r,
                NULL
                ) < 0)
                return -1;
        }
    } else {
        if (PyAwaitable_AddAwait(
            awaitable,
            coro,
            handle_route_callback,
            route_error
            ) < 0) {
            return -1;
        }
    }

    return 0;
}

static int body_inc_buf(PyObject* awaitable, PyObject* result) {
    PyObject* body = PyDict_GetItemString(
        result,
        "body"
    );

    if (!body) {
        return PyErr_BadASGI();
    }

    PyObject* more_body = PyDict_GetItemString(
        result,
        "more_body"
    );
    if (!more_body) {
        Py_DECREF(body);
        return PyErr_BadASGI();
    }

    char* buf_inc;
    Py_ssize_t buf_inc_size;

    if (PyBytes_AsStringAndSize(
        body,
        &buf_inc,
        &buf_inc_size
        ) < 0) {
        Py_DECREF(body);
        Py_DECREF(more_body);
        return -1;
    }

    char* buf;
    Py_ssize_t* size;
    char* query;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &buf,
        &size,
        &query
        ) < 0) {
        Py_DECREF(body);
        Py_DECREF(more_body);
        return -1;
    }

    char* nbuf = realloc(
        buf,
        (*size) + buf_inc_size
    );

    if (!nbuf) {
        Py_DECREF(body);
        Py_DECREF(more_body);
        return -1;
    }

    strcat(
        nbuf,
        buf_inc
    );
    PyAwaitable_SetArbValue(
        awaitable,
        0,
        nbuf
    );
    *size = (*size) + buf_inc_size;

    PyObject* aw;
    PyObject* receive;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &aw,
        &receive
        ) < 0) {
        Py_DECREF(more_body);
        Py_DECREF(body);
        return -1;
    }

    if (PyObject_IsTrue(more_body)) {
        PyObject* receive_coro = PyObject_CallNoArgs(receive);

        if (PyAwaitable_AddAwait(
            awaitable,
            receive_coro,
            body_inc_buf,
            NULL
            ) < 0) {
            Py_DECREF(more_body);
            Py_DECREF(body);
            Py_DECREF(receive_coro);
            free(query);
            free(nbuf);
            return -1;
        }

        Py_DECREF(receive_coro);
    } else {
        if (handle_route_impl(
            aw,
            nbuf,
            query
            ) < 0) {
            Py_DECREF(more_body);
            Py_DECREF(body);
            free(nbuf);
            return -1;
        };
    }

    Py_DECREF(more_body);
    Py_DECREF(body);

    return 0;
}

static int handle_route_query(PyObject* awaitable, char* query) {
    ViewApp* self;
    route* r;
    PyObject** path_params;
    Py_ssize_t* size;
    PyObject* scope;
    PyObject* receive;
    PyObject* send;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        &scope,
        &receive,
        &send,
        NULL
        ) < 0) {
        return -1;
    }

    PyObject* query_obj = query_parser(
        &self->parsers,
        query
    );

    if (!query_obj) {
        PyErr_Clear();
        return server_err(
            self,
            awaitable,
            400,
            r,
            NULL
        );
    }

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        &path_params,
        &size,
        NULL
        ) < 0) {
        Py_DECREF(query_obj);
        return -1;
    }

    Py_ssize_t fake_size = 0;

    if (size == NULL)
        size = &fake_size;
    PyObject** params = calloc(
        r->inputs_size,
        sizeof(PyObject*)
    );
    if (!params) {
        Py_DECREF(query_obj);
        return -1;
    }
    Py_ssize_t final_size = 0;

    for (int i = 0; i < r->inputs_size; i++) {
        if (r->inputs[i]->route_data) {
            PyObject* data = build_data_input(
                r->inputs[i]->route_data,
                scope,
                receive,
                send
            );
            if (!data) {
                for (int i = 0; i < r->inputs_size; i++)
                    Py_XDECREF(params[i]);

                free(params);
                Py_DECREF(query_obj);
                return -1;
            }

            params[i] = data;
            ++final_size;
            continue;
        }

        PyObject* item = PyDict_GetItemString(
            query_obj,
            r->inputs[i]->name
        );

        if (!item) {
            if (r->inputs[i]->df) {
                params[i] = r->inputs[i]->df;
                ++final_size;
                continue;
            }

            for (int i = 0; i < r->inputs_size; i++)
                Py_XDECREF(params[i]);

            free(params);
            Py_DECREF(query_obj);
            return fire_error(
                self,
                awaitable,
                400,
                r,
                NULL,
                NULL
            );
        } else ++final_size;

        if (item) {
            PyObject* parsed_item = cast_from_typecodes(
                r->inputs[i]->types,
                r->inputs[i]->types_size,
                item,
                self->parsers.json,
                true
            );
            if (!parsed_item) {
                PyErr_Clear();
                for (int i = 0; i < r->inputs_size; i++)
                    Py_XDECREF(params[i]);

                free(params);
                Py_DECREF(query_obj);
                return fire_error(
                    self,
                    awaitable,
                    400,
                    r,
                    NULL,
                    NULL
                );
            }
            params[i] = parsed_item;
        }
    }

    PyObject** merged = PyMem_Calloc(
        final_size + (*size),
        sizeof(PyObject*)
    );

    if (!merged) {
        PyErr_NoMemory();
        return -1;
    }

    for (int i = 0; i < (*size); i++)
        merged[i] = path_params[i];

    for (int i = 0; i < final_size; i++)
        merged[*size + i] = params[i];

    for (int i = 0; i < r->middleware_size; i++) {
        PyObject* res = PyObject_Vectorcall(
            r->middleware[i],
            merged,
            *size +
            final_size,
            NULL
        );
        if (!res) {
            if (server_err(
                self,
                awaitable,
                500,
                r,
                NULL
                ) < 0) {
                for (int x = 0; x < final_size + *size; x++)
                    Py_XDECREF(merged[x]);

                PyMem_Free(merged);
                free(params);
                Py_DECREF(query_obj);
                return -1;
            }
            return 0;
        }

        if (PyCoro_CheckExact(res)) {
            if (PyAwaitable_AddAwait(
                awaitable,
                res,
                NULL,
                route_error
                ) < 0) {
                if (server_err(
                    self,
                    awaitable,
                    500,
                    r,
                    NULL
                    ) < 0) {
                    for (int x = 0; x < final_size + *size; x++)
                        Py_XDECREF(merged[x]);

                    PyMem_Free(merged);
                    free(params);
                    Py_DECREF(query_obj);
                    return -1;
                }
                return 0;
            }
        }
    }

    PyObject* coro = PyObject_VectorcallDict(
        r->callable,
        merged,
        *size + final_size,
        NULL
    );

    for (int i = 0; i < final_size + *size; i++)
        Py_XDECREF(merged[i]);

    PyMem_Free(merged);
    free(params);
    Py_DECREF(query_obj);

    if (!coro)
        return -1;

    if (!Py_IS_TYPE(
        coro,
        &PyCoro_Type
        )) {
        if (handle_route_callback(
            awaitable,
            coro
            ) < 0) {
            if (server_err(
                self,
                awaitable,
                500,
                r,
                NULL
                ) < 0)
                return -1;
        }
    } else {
        if (PyAwaitable_AddAwait(
            awaitable,
            coro,
            handle_route_callback,
            route_error
            ) < 0) {
            Py_DECREF(coro);
            return -1;
        }
    }

    Py_DECREF(coro);
    return 0;
}

static int handle_route(PyObject* awaitable, char* query) {
    PyObject* receive;
    route* r;

    if (PyAwaitable_UnpackValues(
        awaitable,
        NULL,
        NULL,
        &receive,
        NULL
        ) < 0)
        return -1;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        NULL,
        NULL,
        NULL
        ) < 0)
        return -1;

    char* buf = malloc(1);         // null terminator

    if (!buf) {
        PyErr_NoMemory();
        return -1;
    }

    Py_ssize_t* size = malloc(sizeof(Py_ssize_t));

    if (!size) {
        free(buf);
        PyErr_NoMemory();
        return -1;
    }

    *size = 1;
    strcpy(
        buf,
        ""
    );

    PyObject* aw = PyAwaitable_New();
    if (!aw) return -1;


    if (PyAwaitable_SaveValues(
        aw,
        2,
        awaitable,
        receive
        ) < 0) {
        Py_DECREF(aw);
        free(buf);
        return -1;
    }

    if (PyAwaitable_SaveArbValues(
        aw,
        3,
        buf,
        size,
        query
        ) < 0) {
        Py_DECREF(aw);
        free(buf);
        return -1;
    }

    PyObject* receive_coro = PyObject_CallNoArgs(receive);

    if (!receive_coro) {
        Py_DECREF(aw);
        return -1;
    }

    if (PyAwaitable_AddAwait(
        aw,
        receive_coro,
        body_inc_buf,
        NULL
        ) < 0) {
        Py_DECREF(aw);
        free(buf);
        return -1;
    }

    Py_DECREF(receive_coro);

    if (PyAwaitable_AWAIT(
        awaitable,
        aw
        ) < 0) {
        Py_DECREF(aw);
        free(buf);
        return -1;
    }

    return 0;
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

    PyObject* raw_path_obj = PyDict_GetItemString(scope, "path");
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
                    NULL
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
                NULL
                ) < 0) {
                Py_DECREF(awaitable);
                free(path);
                return NULL;
            }
            free(path);
            return awaitable;
        }
        // begin path parameter extraction

        char* token;
        map* target = ptr;
        route* rt = NULL;
        bool did_save = false;
        params = calloc(
            1,
            sizeof(PyObject*)
        );
        if (!params) {
            Py_DECREF(awaitable);
            free(size);
            free(path);
            return PyErr_NoMemory();
        }
        bool skip = true;         // skip leading /
        route* last_r = NULL;

        while ((token = v_strsep(
            &path,
            "/"
                        ))) {
            if (skip) {
                skip = false;
                continue;
            }
            // TODO: optimize this
            char* s = malloc(strlen(token) + 2);
            sprintf(
                s,
                "/%s",
                token
            );
            assert(target);

            if ((!did_save && rt && rt->r) || last_r) {
                printf(
                    "last_r: %p\n",
                    last_r
                );
                route* this_r = (last_r ? last_r : rt)->r;
                last_r = this_r;

                PyObject* unicode = PyUnicode_FromString(token);
                if (!unicode) {
                    free(path);
                    Py_DECREF(awaitable);
                    free(size);
                    for (int i = 0; i < *size; i++)
                        Py_DECREF(params[i]);

                    free(params);
                    return NULL;
                }

                params = realloc(
                    params,
                    (++(*size)) * sizeof(PyObject*)
                );
                params[*size - 1] = unicode;
                if (this_r->routes) target = this_r->routes;
                if (!this_r->r) last_r = NULL;
                did_save = true;         // prevent this code from looping, but also preserve rt in case the iteration ends
                continue;
            } else if (did_save) did_save = false;

            rt = map_get(
                target,
                s
            );
            free(s);

            if (!rt) {
                // the route doesnt exist!
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                free(params);
                free(size);
                free(path);
                if (fire_error(
                    self,
                    awaitable,
                    404,
                    NULL,
                    NULL,
                    NULL
                    ) < 0) {
                    Py_DECREF(awaitable);
                    return NULL;
                }

                free(path);
                return awaitable;
            }

            target = rt->routes;
        }

        bool failed = false;
        r = rt->r;
        if (r && !r->callable) {
            r = r->r;         // edge case
            if (!r) failed = true;
        } else if (!r) failed = true;

        if (failed) {
            for (int i = 0; i < *size; i++)
                Py_DECREF(params[i]);

            free(params);
            free(path);
            free(size);
            if (fire_error(
                self,
                awaitable,
                404,
                NULL,
                NULL,
                NULL
                ) < 0) {
                Py_DECREF(awaitable);
                return NULL;
            }
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
        } else {
            for (int i = 0; i < r->middleware_size; i++) {
                PyObject* res = PyObject_CallNoArgs(r->middleware[i]);
                if (PyCoro_CheckExact(res)) {
                    if (PyAwaitable_AddAwait(
                        awaitable,
                        res,
                        NULL,
                        route_error
                        ) < 0) {
                        Py_DECREF(awaitable);
                        Py_DECREF(res);
                        return NULL;
                    };
                }
            }
            res_coro = PyObject_CallNoArgs(r->callable);
        }

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
                NULL
                ) < 0)
                return NULL;
            return awaitable;
        }

        if (!Py_IS_TYPE(
            res_coro,
            &PyCoro_Type
            )) {
            if (handle_route_callback(
                awaitable,
                res_coro
                ) < 0) {
                if (server_err(
                    self,
                    awaitable,
                    500,
                    r,
                    NULL
                    ) < 0)
                    return NULL;
                return awaitable;
            };
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

static int load_errors(route* r, PyObject* dict) {
    PyObject* iter = PyObject_GetIter(dict);
    PyObject* key;
    PyObject* value;

    while ((key = PyIter_Next(iter))) {
        value = PyDict_GetItem(
            dict,
            key
        );
        if (!value) {
            Py_DECREF(iter);
            return -1;
        }

        int status_code = PyLong_AsLong(key);
        if (status_code == -1) {
            Py_DECREF(iter);
            return -1;
        }


        if (status_code < 400 || status_code > 511) {
            PyErr_Format(
                PyExc_ValueError,
                "%d is not a valid status code",
                status_code
            );
            Py_DECREF(iter);
            return -1;
        }

        if (status_code >= 500) {
            r->server_errors[status_code - 500] = Py_NewRef(value);
        } else {
            uint16_t index = hash_client_error(status_code);
            if (index == 600) {
                PyErr_Format(
                    PyExc_ValueError,
                    "%d is not a valid status code",
                    status_code
                );
                return -1;
            }
            r->client_errors[index] = Py_NewRef(value);
        }
    }

    Py_DECREF(iter);

    if (PyErr_Occurred()) return -1;
    return 0;
}

static inline int bad_input(const char* name) {
    PyErr_Format(
        PyExc_ValueError,
        "missing key in loader dict: %s",
        name
    );
    return -1;
}


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


static int load(
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

static bool figure_has_body(PyObject* inputs) {
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

int load_parts(ViewApp* app, map* routes, PyObject* parts, route* r) {
    PyObject* iter = PyObject_GetIter(parts);
    if (!iter) return -1;

    PyObject* item;
    map* target = routes;
    route* rt = NULL;
    Py_ssize_t size = PySequence_Size(parts);
    if (size == -1) {
        Py_DECREF(iter);
        return -1;
    }

    Py_ssize_t index = 0;
    bool set_r = false;

    while ((item = PyIter_Next(iter))) {
        ++index;

        if (PyUnicode_CheckExact(
            item
            )) {
            // path part
            const char* str = PyUnicode_AsUTF8(item);
            if (!str) {
                Py_DECREF(iter);
                return -1;
            };
            route* found = map_get(
                target,
                str
            );
            route* transport = route_transport_new(NULL);
            if (!transport) {
                Py_DECREF(iter);
                return -1;
            };
            if (!found) {
                map_set(
                    target,
                    str,
                    transport
                );
                transport->routes = TRANSPORT_MAP();
                target = transport->routes;
                if (!target) {
                    Py_DECREF(iter);
                    return -1;
                };
            } else {
                if (!found->routes) found->routes = TRANSPORT_MAP();
                if (!found->routes) {
                    Py_DECREF(iter);
                    return -1;
                };
                target = found->routes;
                map_set(
                    target,
                    str,
                    transport
                );
            }
            rt = transport;
        } else {
            app->has_path_params = true;
            if (!rt) VIEW_FATAL("first path param was part");
            if (index == size) {
                rt->r = r;
                set_r = true;
            } else {
                rt->r = route_transport_new(NULL);
                rt = rt->r;
            }
        }
        if (!set_r) rt->r = r;
    }

    Py_DECREF(iter);
    if (PyErr_Occurred()) return -1;

    return 0;
}

static int load_middleware(route* r, PyObject* list) {
    Py_ssize_t size = PyList_GET_SIZE(list);
    PyObject** middleware = PyMem_Calloc(
        size,
        sizeof(PyObject*)
    );
    r->middleware_size = size;

    if (!middleware) {
        PyErr_NoMemory();
        return -1;
    }

    for (int i = 0; i < size; i++) {
        PyObject* func = PyList_GET_ITEM(
            list,
            i
        );
        middleware[i] = Py_NewRef(func);
    }

    r->middleware = middleware;
    return 0;
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
