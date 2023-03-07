#include <Python.h>
#include <view/app.h>
#include <view/awaitable.h>
#include <view/map.h>
#include <stdbool.h>
#define LOAD_ROUTE(target) char* path; \
    PyObject* cb; \
    int flags; \
    if (!PyArg_ParseTuple( \
    args, \
    "sOi", \
    &path, \
    &cb \
        )) return NULL; \
    route* r = route_new( \
    cb, \
    flags, \
    2 \
               ); \
    if (!r) return NULL; \
    map_set( \
    self->target, \
    path, \
    r \
    ); \
    Py_RETURN_NONE;
#define ROUTE(target) static PyObject* target ( \
    ViewApp * self, \
    PyObject * args \
) { \
        LOAD_ROUTE(target); \
}

typedef struct {
    PyObject_HEAD;
    PyObject* startup;
    PyObject* cleanup;
    map* get;
    map* post;
    map* put;
    map* patch;
    map* delete;
    PyObject* client_errors[32];
    PyObject* server_errors[11];
    bool dev;
} ViewApp;


typedef struct {
    PyObject* callable;
    char* cache;
    PyObject* cache_headers;
    uint16_t cache_status;
    route_flags flags;
    Py_ssize_t cache_index;
    Py_ssize_t cache_rate;
} route;

route* route_new(PyObject* callable, route_flags f, Py_ssize_t cache_rate) {
    route* r = malloc(sizeof(route));
    if (!r) return (route*) PyErr_NoMemory();

    r->cache = NULL;
    r->callable = Py_NewRef(callable);
    r->flags = f;
    r->cache_rate = cache_rate;
    r->cache_index = 0;
    r->cache_headers = NULL;
    r->cache_status = 0;
    return r;
}

void route_free(route* r) {
    Py_XDECREF(r->cache_headers);
    Py_DECREF(r->callable);
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

    return (PyObject*) self;
}

static int init(PyObject* self, PyObject* args, PyObject* kwds) {
    PyErr_SetString(
        PyExc_TypeError,
        "ViewApp is not constructable"
    );
    return -1;
}

static int fire_error(ViewApp* self, PyObject* awaitable, int status) {
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

    PyObject* send_coro = PyObject_CallFunction(
        send,
        "{s:s}",
        "type",
        is_startup ? "lifespan.startup.complete" : "lifespan.shutdown.complete"
    );

    if (!send_coro)
        return -1;

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

    for (int i = 0; i < 11; i++)
        Py_XDECREF(self->server_errors[i]);

    for (int i = 0; i < 32; i++)
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
    if (tp && value && tp) {
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

    ViewApp* self;
    PyObject* send;
    if (PyAwaitable_UnpackValues(
        awaitable,
        &self,
        NULL,
        NULL,
        &send
        ) < 0) return -1;


    PyObject* coro = PyObject_CallFunction(
        send,
        "{s:s,s:i,s:[[yy]]}",
        "type",
        "http.response.start",
        "status",
        500,
        "headers",
        "content-type",
        "text/plain"
    );

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

    bool should_free = false;
    char* response;

    if (self->dev) {
        response = malloc(512);
        should_free = true;

        if (!response) {
            PyErr_NoMemory();
            return -1;
        }

        PyObject* value_str_ob;
        const char* value_str;
        if (value) {
            value_str_ob = PyObject_Str(value);
            if (!value_str_ob) return -1;
            value_str = PyUnicode_AsUTF8(value_str_ob);
            if (!value_str) return -1;
        }

        snprintf(
            response,
            512,
            "%s%s%s%s",
            ((PyTypeObject*) tp)->tp_name,
            value ? ":" : "",
            value ? " " : "",
            value ? value_str : ""
        );
    } else {
        response = "Internal error!";
    }
    coro = PyObject_CallFunction(
        send,
        "{s:s,s:y}",
        "type",
        "http.response.body",
        "body",
        response
    );

    if (should_free) free(response);
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
    if (r->cache_rate > 0) {
        r->cache = res_str;
        r->cache_status = status;
        r->cache_headers = Py_NewRef(headers);
        r->cache_index = 0;
    }

    PyObject* coro = PyObject_CallFunction(
        send,
        "{s:s,s:i,s:O}",
        "type",
        "http.response.start",
        "status",
        status,
        "headers",
        headers
    );

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

    coro = PyObject_CallFunction(
        send,
        "{s:s,s:y}",
        "type",
        "http.response.body",
        "body",
        res_str
    );

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

    if (!ptr) {
        PyErr_BadArgument();
        return NULL;
    }

    route* r = map_get(
        ptr,
        path
    );

    if ((r->cache_index++ < r->cache_rate) && r->cache) {
        PyObject* coro = PyObject_CallFunction(
            send,
            "{s:s,s:i,s:O}",
            "type",
            "http.response.start",
            "status",
            r->cache_status,
            "headers",
            r->cache_headers
        );

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

        coro = PyObject_CallFunction(
            send,
            "{s:s,s:y}",
            "type",
            "http.response.body",
            "body",
            r->cache
        );

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

    if (!r) {
        PyErr_Format(
            PyExc_RuntimeError,
            "not found: %s",
            path
        );
        Py_DECREF(awaitable);
        return NULL;
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

ROUTE(get);
ROUTE(post);
ROUTE(patch);
ROUTE(put);
ROUTE(delete);

static PyObject* exc_handler(ViewApp* self, PyObject* args) {
    PyObject* handler;
    int status_code;

    if (!PyArg_ParseTuple(
        args,
        "iO",
        &status_code,
        &handler
        )) return NULL;
    if ((status_code < 400 || status_code > 511) || (status_code > 431 &&
                                                     status_code < 451) ||
        (status_code > 451 && status_code < 500))
        return PyErr_Format(
            PyExc_ValueError,
            "%d is not a valid status code for error handling",
            status_code
        );

    if (status_code > 499) {
        self->server_errors[status_code - 501] = Py_NewRef(handler);
    } else {
        if (status_code == 451)
            self->client_errors[31] = Py_NewRef(handler);
        else
            self->client_errors[status_code - 401] = Py_NewRef(handler);
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
    {"_set_dev_state", (PyCFunction) set_dev_state, METH_VARARGS, NULL},
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
