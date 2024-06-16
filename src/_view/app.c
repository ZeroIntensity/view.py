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
        int* num = PyMem_Malloc(sizeof(int)); \
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

int view_PyErr_BadASGI(char* file, int lineno) {
    PyErr_Format(
        PyExc_RuntimeError,
        "(%s:%d) problem with view.py's ASGI server (this is a bug!)",
        file,
        lineno
    );
    return -1;
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
        path = PyMem_Malloc(len);
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
        PyMem_Free(path);
        return NULL;
    }

    const char* query_str = PyBytes_AsString(query_obj);

    if (!query_str) {
        Py_DECREF(awaitable);
        PyMem_Free(path);
        return NULL;
    }
    char* query = strdup(query_str);
    map* ptr = self->websocket; // ws by default
    const char* method_str = "websocket";

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
        if (ptr == self->websocket) {
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
                    method_str,
                    is_http
                    ) < 0) {
                    Py_DECREF(awaitable);
                    PyMem_Free(path);
                    return NULL;
                }
                PyMem_Free(path);
                return awaitable;
            }
            if (fire_error(
                self,
                awaitable,
                404,
                NULL,
                NULL,
                NULL,
                method_str,
                is_http
                ) < 0) {
                Py_DECREF(awaitable);
                PyMem_Free(path);
                return NULL;
            }
            PyMem_Free(path);
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
            PyMem_Free(path);
            PyMem_Free(size);

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

                PyMem_Free(params);
                PyMem_Free(size);
            }
            PyMem_Free(path);
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

                PyMem_Free(params);
                PyMem_Free(size);
            }
            PyMem_Free(path);
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

                PyMem_Free(params);
                PyMem_Free(size);
            }
            Py_DECREF(awaitable);
            Py_DECREF(coro);
            PyMem_Free(path);
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

                PyMem_Free(params);
                PyMem_Free(size);
            }
            Py_DECREF(awaitable);
            PyMem_Free(path);
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

                PyMem_Free(params);
                PyMem_Free(size);
            }
            Py_DECREF(awaitable);
            PyMem_Free(path);
            return NULL;
        }

        if (PyAwaitable_AWAIT(
            awaitable,
            coro
            ) < 0) {
            if (size) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                PyMem_Free(params);
                PyMem_Free(size);
            }
            Py_DECREF(awaitable);
            Py_DECREF(coro);
            PyMem_Free(path);
            return NULL;
        }

        Py_DECREF(coro);
        PyMem_Free(path);
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
                PyMem_Free(path);
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
        // If there are no inputs, we can skip parsing!
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

            PyMem_Free(path);
            PyMem_Free(params);
            PyMem_Free(size);
        } else res_coro = PyObject_CallNoArgs(r->callable);

        if (!res_coro) {
            Py_DECREF(awaitable);
            PyMem_Free(path);
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
            PyMem_Free(path);
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
