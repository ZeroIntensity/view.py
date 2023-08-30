#include <view/app.h>
#include <view/awaitable.h>
#include <view/map.h>
#include <stdbool.h>
#include <stdint.h>
#define ER(code, str) case code: return str
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
    if (load( \
        r, \
        inputs \
        ) < 0) return NULL; \
    if (load_errors(r, errors) < 0) \
        return NULL; \
    if (!PySequence_Size(parts)) \
        map_set(self-> target, path, r); \
    else \
        if (load_parts(self, self-> target, parts, r) < 0) return NULL; \
    Py_RETURN_NONE;
#define TRANSPORT_MAP() map_new(2, (map_free_func) route_free)

#define ROUTE(target) static PyObject* target ( \
    ViewApp* self, \
    PyObject* args \
) { \
        LOAD_ROUTE(target); \
}
#define ERR(code, msg) case code: return send_raw_text( \
    awaitable, \
    send, \
    code, \
    msg \
    );

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
    PyObject* client_errors[28];
    PyObject* server_errors[11];
    bool dev;
    PyObject* exceptions;
    app_parsers parsers;
    bool has_path_params;
} ViewApp;

typedef struct _route_input {
    PyObject* type;
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
    bool pass_context;
    bool has_body;
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

static int PyErr_BadASGI(void) {
    PyErr_SetString(
        PyExc_RuntimeError,
        "error with asgi implementation"
    );
    return -1;
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
    r->pass_context = false;
    r->has_body = has_body;

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
        Py_DECREF(r->inputs[i]->df);
        Py_DECREF(r->inputs[i]->type);

        for (int i = 0; i < r->inputs[i]->validators_size; i++) {
            Py_DECREF(r->inputs[i]->validators[i]);
        }
    }

    PyMem_Free(r->inputs);
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
    printf("type: ");
    PyObject_Print(
        ri->type,
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
    rt->pass_context = false;
    rt->has_body = false;

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

static PyObject** json_parser(
    app_parsers* parsers,
    const char* data,
    PyObject* query,
    route_input** inputs,
    Py_ssize_t inputs_size
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
        PyObject* item = PyDict_GetItemString(
            inp->is_body ? obj : query,
            inp->name
        );

        if (!item) {
            Py_DECREF(obj);
            free(ob);
            return NULL;
        }

        if (inp->type) {
            /*
               if (!PyObject_IsInstance(
                item,
                inp->type
                )) {
                return NULL;
               }
             */
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

    if (!self->options || !self->patch || !self->delete || !self->post ||
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
    PyObject* headers /* may be NULL */
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

    return 600;
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

    Py_FatalError("got bad status code");
}

static int find_result_for(
    PyObject* target,
    char** res_str,
    int* status,
    PyObject* headers
) {
    PyObject* view_result = PyObject_GetAttrString(
        target,
        "__view_result__"
    );

    if (Py_IS_TYPE(
        target,
        &PyUnicode_Type
        ) || view_result) {
        PyObject* str_target;

        if (view_result) {
            str_target = PyObject_CallNoArgs(view_result);
            if (!str_target) return -1;
            if (!Py_IS_TYPE(
                str_target,
                &PyUnicode_Type
                )) {
                PyErr_Format(
                    PyExc_TypeError,
                    "%R.__view_result__ returned %R, expected str instance",
                    target,
                    str_target
                );
            }
        } else str_target = target;

        const char* tmp = PyUnicode_AsUTF8(str_target);
        if (!tmp) return -1;
        *res_str = strdup(tmp);
    } else if (Py_IS_TYPE(
        target,
        &PyDict_Type
               )) {
        PyObject* iter = PyObject_GetIter(target);
        if (!iter) return -1;
        PyObject* item;
        while ((item = PyIter_Next(iter))) {
            PyObject* v = PyDict_GetItem(
                target,
                item
            );
            if (!v) {
                Py_DECREF(iter);
                return -1;
            }
            PyObject* v_str = PyObject_Str(v);
            if (v_str) {
                Py_DECREF(iter);
                return -1;
            }
            PyObject* item_str = PyObject_Str(item);
            if (!item_str) {
                Py_DECREF(v_str);
                Py_DECREF(iter);
                return -1;
            }

            PyObject* v_bytes = PyBytes_FromObject(v_str);
            if (!v_bytes) {
                Py_DECREF(v_str);
                Py_DECREF(iter);
                Py_DECREF(item_str);
                return -1;
            }
            PyObject* item_bytes = PyBytes_FromObject(item_str);
            if (!item_bytes) {
                Py_DECREF(v_bytes);
                Py_DECREF(v_str);
                Py_DECREF(iter);
                Py_DECREF(item_str);
                return -1;
            }

            PyObject* header_list = PyList_New(2);
            if (PyList_Append(
                header_list,
                item_bytes
                ) < 0) {
                Py_DECREF(header_list);
                Py_DECREF(item_str);
                Py_DECREF(iter);
                Py_DECREF(v_str);
                Py_DECREF(item_bytes);
                Py_DECREF(v_bytes);
            };

            if (PyList_Append(
                header_list,
                v_bytes
                ) < 0) {
                Py_DECREF(header_list);
                Py_DECREF(item_str);
                Py_DECREF(iter);
                Py_DECREF(v_str);
                Py_DECREF(item_bytes);
                Py_DECREF(v_bytes);
            };

            Py_DECREF(item_str);
            Py_DECREF(v_str);
            Py_DECREF(item_bytes);
            Py_DECREF(v_bytes);

            if (PyList_Append(
                headers,
                header_list
                ) < 0) {
                Py_DECREF(header_list);
                return -1;
            }
        }

        Py_DECREF(iter);
        if (PyErr_Occurred()) return -1;
    } else if (Py_IS_TYPE(
        target,
        &PyLong_Type
               )) {
        *status = (int) PyLong_AsLong(target);
    } else {
        PyErr_SetString(
            PyExc_TypeError,
            "returned tuple should only contain a str, int, or dict"
        );
        return -1;
    }

    return 0;
}
static int handle_result(
    PyObject* result,
    char** res_target,
    int* status_target,
    PyObject** headers_target
) {
    char* res_str = NULL;
    int status = 200;
    PyObject* headers = PyList_New(0);

    if (PyObject_IsInstance(
        result,
        (PyObject*) &PyUnicode_Type
        )) {
        const char* tmp = PyUnicode_AsUTF8(result);
        if (!tmp) return -1;
        res_str = strdup(tmp);
    } else if (PyObject_IsInstance(
        result,
        (PyObject*) &PyTuple_Type
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

            if (second && find_result_for(
                second,
                &res_str,
                &status,
                headers
                ) < 0) return -1;
        }
    } else {
        PyObject* view_result = PyObject_GetAttrString(
            result,
            "__view_result__"
        );
        if (view_result) {
            PyObject* str = PyObject_CallNoArgs(view_result);
            if (!str) return -1;
            if (!Py_IS_TYPE(
                str,
                &PyUnicode_Type
                )) {
                PyErr_Format(
                    PyExc_TypeError,
                    "%R.__view_result__ returned %R, expected str instance",
                    view_result,
                    str
                );
            }
            const char* tmp = PyUnicode_AsUTF8(str);
            if (!tmp) return -1;
            res_str = strdup(tmp);
        } else {
            PyErr_Format(
                PyExc_TypeError,
                "%R is not a valid return value for route",
                result
            );
            return -1;
        }
    }

    *res_target = res_str;
    *status_target = status;
    *headers_target = headers;
    return 0;
}

static int finalize_err_cb(PyObject* awaitable, PyObject* result) {
    PyObject* send;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &send
        ) < 0) {
        return -1;
    }

    char* res_str;
    int status_code;
    PyObject* headers;

    if (handle_result(
        result,
        &res_str,
        &status_code,
        &headers
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
    bool* called
) {
    if (!handler) {
        if (called) *called = false;
        if (send_raw_text(
            awaitable,
            send,
            status,
            get_err_str(status),
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
        1,
        send
        ) < 0) {
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
    bool* called
) {
    PyObject* send;
    if (PyAwaitable_UnpackValues(
        awaitable,
        NULL,
        NULL,
        NULL,
        &send
        ) < 0)
        return -1;

    uint16_t index = 0;
    PyObject* handler = NULL;


    if (status >= 500) {
        index = status - 500;
        if (r) handler = r->server_errors[index];
        if (!handler) handler = self->server_errors[index];
    } else {
        index = hash_client_error(status);
        if (index == 600) {
            PyErr_BadInternalCall();
            return -1;
        };
        if (r) handler = r->client_errors[index];
        if (!handler) handler = self->client_errors[index];
    }

    if (run_err_cb(
        awaitable,
        handler,
        send,
        status,
        called
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
    Py_XDECREF(self->exceptions);

    for (int i = 0; i < 11; i++)
        Py_XDECREF(self->server_errors[i]);

    for (int i = 0; i < 28; i++)
        Py_XDECREF(self->client_errors[i]);

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

static int route_error(
    PyObject* awaitable,
    PyObject* tp,
    PyObject* value,
    PyObject* tb
) {
    ViewApp* self;
    route* r;
    bool handler_was_called;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        NULL,
        NULL,
        NULL
        ) < 0) return -1;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        NULL,
        NULL
        ) < 0) return -1;


    if (fire_error(
        self,
        awaitable,
        500,
        r,
        &handler_was_called
        ) < 0) {
        return -1;
    }

    if (!handler_was_called) {
        PyErr_NormalizeException(
            &tp,
            &value,
            &tb
        );
        PyErr_Display(
            tp,
            value,
            tb
        );
    }

    return 0;
}


static int handle_route_callback(PyObject* awaitable,
                                 PyObject* result) {
    PyObject* send;
    route* r;

    if (PyAwaitable_UnpackValues(
        awaitable,
        NULL,
        NULL,
        NULL,
        &send
        ) < 0) return -1;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        NULL,
        NULL
        ) < 0) return -1;

    char* res_str;
    int status;
    PyObject* headers;

    if (handle_result(
        result,
        &res_str,
        &status,
        &headers
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

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        NULL,
        NULL,
        NULL
        ) < 0) {
        return -1;
    }

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        &path_params,
        &size
        ) < 0) {
        return -1;
    }

    PyObject* query_obj = query_parser(
        &self->parsers,
        query
    );

    if (!query_obj) {
        PyErr_Clear();
        return fire_error(
            self,
            awaitable,
            400,
            r,
            NULL
        );
    }


    PyObject** params = json_parser(
        &self->parsers,
        body,
        query_obj,
        r->inputs,
        r->inputs_size
    );

    Py_DECREF(query_obj);

    if (!params) {
        // parsing failed
        PyErr_Clear();

        return fire_error(
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
    } else {
        coro = PyObject_Vectorcall(
            r->callable,
            params,
            r->inputs_size,
            NULL
        );

        for (int i = 0; i < r->inputs_size; i++) {
            Py_DECREF(params[i]);
        }
    }

    if (!coro) {
        return -1;
    }

    if (PyAwaitable_AddAwait(
        awaitable,
        coro,
        handle_route_callback,
        route_error
        ) < 0) {
        return -1;
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

    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        NULL,
        NULL,
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
        return fire_error(
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
        &size
        ) < 0) {
        Py_DECREF(query_obj);
        return -1;
    }

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
            for (int i = 0; i < r->inputs_size; i++) {
                Py_XDECREF(params[i]);
            }

            free(params);
            Py_DECREF(query_obj);
            return fire_error(
                self,
                awaitable,
                400,
                r,
                NULL
            );
        } else {
            ++final_size;
        }

        if (item)
            params[i] = Py_NewRef(item);
    }

    PyObject** merged = calloc(
        final_size + (*size),
        sizeof(PyObject*)
    );

    for (int i = 0; i < (*size); i++)
        merged[i] = path_params[i];

    for (int i = 0; i < final_size; i++)
        merged[*size + i] = params[i];

    PyObject* coro = PyObject_VectorcallDict(
        r->callable,
        merged,
        *size + final_size,
        NULL
    );

    for (int i = 0; i < final_size + *size; i++)
        Py_XDECREF(merged[i]);


    free(params);
    Py_DECREF(query_obj);

    if (!coro)
        return -1;

    if (PyAwaitable_AddAwait(
        awaitable,
        coro,
        handle_route_callback,
        route_error
        ) < 0) {
        Py_DECREF(coro);
        return -1;
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

static PyObject* app(ViewApp* self, PyObject* const* args, Py_ssize_t
                     nargs) {
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

    const char* raw_path = dict_get_str(
        scope,
        "path"
    );
    if (!raw_path) {
        Py_DECREF(awaitable);
        return NULL;
    }
    const char* method = dict_get_str(
        scope,
        "method"
    );
    if (!method) {
        Py_DECREF(awaitable);
        return NULL;
    }

    PyObject* query_obj = PyDict_GetItemString(
        scope,
        "query_string"
    );

    if (!query_obj) {
        Py_DECREF(awaitable);
        return NULL;
    }

    const char* query_str = PyBytes_AsString(query_obj);

    if (!query_str) {
        Py_DECREF(awaitable);
        return NULL;
    }

    char* query = strdup(query_str);

    map* ptr = NULL;
    if (!strcmp(
        method,
        "GET"
        ))
        ptr = self->get;
    else if (!strcmp(
        method,
        "POST"
             ))
        ptr = self->post;
    else if (!strcmp(
        method,
        "PATCH"
             ))
        ptr = self->patch;
    else if (!strcmp(
        method,
        "PUT"
             ))
        ptr = self->put;
    else if (!strcmp(
        method,
        "DELETE"
             ))
        ptr = self->delete;
    else if (!strcmp(
        method,
        "OPTIONS"
             )) ptr = self->options;

    if (!ptr) {
        ptr = self->get;
    }

    size_t len = strlen(raw_path);
    char* path;

    if (raw_path[len - 1] == '/' && len != 1) {
        path = malloc(len);
        if (!path) {
            Py_DECREF(awaitable);
            return PyErr_NoMemory();
        }

        for (int i = 0; i < len - 1; i++)
            path[i] = raw_path[i];

        path[len - 1] = '\0';
    } else {
        path = strdup(raw_path);
        if (!path) {
            Py_DECREF(awaitable);
            return PyErr_NoMemory();
        }
    }
    route* r = map_get(
        ptr,
        path
    );
    PyObject** params = NULL;
    Py_ssize_t* size = NULL;

    if (!r) {
        if (!self->has_path_params) {
            if (fire_error(
                self,
                awaitable,
                404,
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
        size = malloc(sizeof(Py_ssize_t));         // so it can be stored in the awaitable
        if (!size) {
            Py_DECREF(awaitable);
            free(path);
            return PyErr_NoMemory();
        }
        *size = 0;
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

        while ((token = strsep(
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
            puts(s);
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

            puts("searching map");
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
                NULL
                ) < 0) {
                Py_DECREF(awaitable);
                return NULL;
            }
        }
        route_print(r);
    }

    if ((r->cache_index++ < r->cache_rate) && r->cache) {
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
        3,
        r,
        params,
        size
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
            res_coro = PyObject_CallNoArgs(r->callable);
        }
        if (!res_coro) {
            Py_DECREF(awaitable);
            free(path);
            return NULL;
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

        inp->type = Py_XNewRef(
            PyDict_GetItemString(
                item,
                "type"
            )
        );

        if (!inp->type) {
            Py_DECREF(iter);
            Py_XDECREF(inp->df);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return bad_input("type");
        }

        PyObject* validators = PyDict_GetItemString(
            item,
            "validators"
        );

        if (!validators) {
            Py_DECREF(iter);
            Py_XDECREF(inp->df);
            Py_DECREF(inp->type);
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
            Py_DECREF(inp->type);
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

    while ((item = PyIter_Next(iter))) {
        PyObject* is_body = PyDict_GetItemString(
            inputs,
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

        if (PyObject_IsInstance(
            item,
            (PyObject*) &PyUnicode_Type
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
            if (!rt) Py_FatalError("first path param was part");
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

ROUTE(get);
ROUTE(post);
ROUTE(patch);
ROUTE(put);
ROUTE(delete);
ROUTE(options);

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

static PyObject* set_dev_state(ViewApp* self, PyObject* args) {
    int value;
    if (!PyArg_ParseTuple(
        args,
        "p",
        &value
        )) return NULL;
    self->dev = (bool) value;
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

static PyMethodDef methods[] = {
    {"asgi_app_entry", (PyCFunction) app, METH_FASTCALL, NULL},
    {"_get", (PyCFunction) get, METH_VARARGS, NULL},
    {"_post", (PyCFunction) post, METH_VARARGS, NULL},
    {"_put", (PyCFunction) put, METH_VARARGS, NULL},
    {"_patch", (PyCFunction) patch, METH_VARARGS, NULL},
    {"_delete", (PyCFunction) delete, METH_VARARGS, NULL},
    {"_options", (PyCFunction) options, METH_VARARGS, NULL},
    {"_set_dev_state", (PyCFunction) set_dev_state, METH_VARARGS, NULL},
    {"_err", (PyCFunction) err_handler, METH_VARARGS, NULL},
    {"_supply_parsers", (PyCFunction) supply_parsers, METH_VARARGS,
     NULL},
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
