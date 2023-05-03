#include <Python.h>
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
    if (!PyArg_ParseTuple( \
        args, \
        "sOnOO", \
        &path, \
        &callable, \
        &cache_rate, \
        &inputs, \
        &errors \
        )) return NULL; \
    route* r = route_new( \
        callable, \
        PySequence_Size(inputs), \
        cache_rate \
    ); \
    if (!r) return NULL; \
    if (load( \
        r, \
        inputs \
        ) < 0) return NULL; \
    if (load_errors(r, errors) < 0) \
        return NULL; \
    map_set(self-> target, path, r); \
    Py_RETURN_NONE;


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

typedef struct {
    PyObject_HEAD;
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
} ViewApp;

typedef struct {
    PyObject* type;
    PyObject* df;
    PyObject** validators;
    Py_ssize_t validators_size;
    char* name;
    bool is_body;
} route_input;

typedef struct {
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
} route;

route* route_new(
    PyObject* callable,
    Py_ssize_t inputs_size,
    Py_ssize_t cache_rate
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

    if (!dict) {
        return -1;
    }

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

    assert(!"got bad status code");
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

    if (!coro) {
        return -1;
    }

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
        is_startup ? "lifespan.startup.complete" : "lifespan.shutdown.complete"
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

    if (!ob) {
        Py_DECREF(dict);
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
        &r
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

    if (!handler_was_called && tp && value && tb) {
        PyErr_WarnEx(
            PyExc_RuntimeWarning,
            "error in route",
            2
        );
        PyErr_Display(
            tp,
            value,
            tb
        );
    }

    return 0;
}



static int handle_route(PyObject* awaitable, PyObject* result) {
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
        &r
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
        Py_DECREF(awaitable);
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

static PyObject* app(ViewApp* self, PyObject* args) {
    PyObject* scope;
    PyObject* receive;
    PyObject* send;
    if (!PyArg_ParseTuple(
        args,
        "OOO",
        &scope,
        &receive,
        &send
        )) return NULL;

    PyObject* tp = PyDict_GetItemString(
        scope,
        "type"
    );
    if (!tp)
        return NULL;

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

    const char* path = dict_get_str(
        scope,
        "path"
    );
    if (!path) {
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

    route* r = map_get(
        ptr,
        path
    );

    if (!r) {
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

        return awaitable;
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
            Py_DECREF(awaitable);
            return NULL;
        }

        if (PyAwaitable_AWAIT(
            awaitable,
            coro
            ) < 0) {
            Py_DECREF(awaitable);
            Py_DECREF(coro);
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
            Py_DECREF(awaitable);
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
            Py_DECREF(awaitable);
            return NULL;
        }

        if (PyAwaitable_AWAIT(
            awaitable,
            coro
            ) < 0) {
            Py_DECREF(awaitable);
            Py_DECREF(coro);
            return NULL;
        }

        Py_DECREF(coro);
        return awaitable;
    }

    PyObject* res_coro = PyObject_CallNoArgs(r->callable);
    if (!res_coro) {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyAwaitable_SaveArbValues(
        awaitable,
        1,
        r
        ) < 0) {
        Py_DECREF(awaitable);
        Py_DECREF(res_coro);
        return NULL;
    }

    if (PyAwaitable_AddAwait(
        awaitable,
        res_coro,
        handle_route,
        route_error
        ) < 0) {
        Py_DECREF(res_coro);
        Py_DECREF(awaitable);
        return NULL;
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
            return -1;
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
            return -1;
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
            return -1;
        }

        inp->type = Py_XNewRef(
            PyDict_GetItemString(
                item,
                "type"
            )
        );
        if (!inp->type) {
            Py_DECREF(iter);
            Py_DECREF(inp->df);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return -1;
        }

        PyObject* validators = PyDict_GetItemString(
            item,
            "validators"
        );

        if (!validators) {
            Py_DECREF(iter);
            Py_DECREF(inp->df);
            Py_DECREF(inp->type);
            PyMem_Free(r->inputs);
            PyMem_Free(inp);
            return -1;
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
            Py_DECREF(inp->df);
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

static PyMethodDef methods[] = {
    {"asgi_app_entry", (PyCFunction) app, METH_VARARGS, NULL},
    {"_get", (PyCFunction) get, METH_VARARGS, NULL},
    {"_post", (PyCFunction) post, METH_VARARGS, NULL},
    {"_put", (PyCFunction) put, METH_VARARGS, NULL},
    {"_patch", (PyCFunction) patch, METH_VARARGS, NULL},
    {"_delete", (PyCFunction) delete, METH_VARARGS, NULL},
    {"_options", (PyCFunction) options, METH_VARARGS, NULL},
    {"_set_dev_state", (PyCFunction) set_dev_state, METH_VARARGS, NULL},
    {"_err", (PyCFunction) err_handler, METH_VARARGS, NULL},
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
