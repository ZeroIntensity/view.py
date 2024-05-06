#include <Python.h>
#include <stdbool.h> // bool

#include <view/app.h> // ViewApp
#include <view/awaitable.h>
#include <view/backport.h>
#include <view/errors.h> // route_error
#include <view/inputs.h> // route_input
#include <view/parsers.h> // body_inc_buf
#include <view/results.h> // handle_result
#include <view/routing.h>

/*
 * -- routes and r information --
 * lets say the requested route is GET /app/12345/index and 12345 is a path parameter.
 * we would first map_get(app->get, "/app"). if this returns NULL, it is a 404.
 * then, we map_get(route->routes, "/12345"). if NULL, we check if a route->r is available.
 * if so, this is a path parameter, we save the value and move on to the next. otherwise, 404.
 * we repeat this process until we reach the end of the URL. so, next we do map_get(route->r->routes, "/index").
 * */

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

int handle_route_impl(
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

    const char* method_str;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        &path_params,
        &size,
        &method_str
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
            NULL,
            method_str
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
            NULL,
            method_str
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
                    NULL,
                    method_str
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
            NULL,
            method_str
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
                    NULL,
                    method_str
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
                        NULL,
                        method_str
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
                NULL,
                method_str
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

int handle_route(PyObject* awaitable, char* query) {
    PyObject* receive;
    route* r;

    if (PyAwaitable_UnpackValues(
        awaitable,
        NULL,
        NULL,
        &receive,
        NULL,
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

int handle_route_callback(
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

int send_raw_text(
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
