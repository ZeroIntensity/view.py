/*
 * view.py C route handling implementation
 *
 * This file contains the the general logic for calling
 * a route object, and where to send their results.
 *
 * This is responsible for determining inputs, dealing with return
 * values, and dispatching the HTTP response to the ASGI server.
 *
 * Raw results returned from a route are one of three things:
 *
 * - A tuple containing a string and integer, and optionally a dictionary.
 * - A string, solely denoting a body.
 * - An object with a __view_result__(), which returns one of the two above.
 *
 * The handling implementation is only responsible for dealing with a __view_result__(), and
 * the rest is sent to the route result implementation.
 */
#include <Python.h>
#include <stdbool.h> // bool

#include <view/app.h> // ViewApp
#include <view/backport.h>
#include <view/context.h> // context_from_data
#include <view/errors.h>  // route_error
#include <view/handling.h>
#include <view/inputs.h>  // route_input, body_inc_buf
#include <view/results.h> // handle_result
#include <view/view.h> // route_log

#include <pyawaitable.h>

// NOTE: This should be below 512 for PyMalloc to be effective
// on the first call.
#define INITIAL_BUF_SIZE 256

/*
 * Call a route object with both query and body parameters.
 */
int
handle_route_impl(
    PyObject *awaitable,
    char *body,
    char *query
)
{
    route *r;
    ViewApp *self;
    Py_ssize_t *size;
    PyObject **path_params;
    PyObject *scope;
    PyObject *receive;
    PyObject *send;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            &self,
            &scope,
            &receive,
            &send,
            NULL
        ) < 0
    )
    {
        return -1;
    }

    const char *method_str;

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &r,
            &path_params,
            &size,
            &method_str
        ) < 0
    )
    {
        return -1;
    }

    PyObject *query_obj = query_parser(
        &self->parsers,
        query
    );

    if (!query_obj)
    {
        show_error(self->dev);
        return server_err(
            self,
            awaitable,
            400,
            r,
            NULL,
            method_str
        );
    }

    PyObject **params = generate_params(
        self,
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

    if (!params)
    {
        show_error(self->dev);
        return server_err(
            self,
            awaitable,
            400,
            r,
            NULL,
            method_str
        );
    }

    PyObject *coro;

    if (size)
    {
        PyObject **merged = PyMem_Calloc(
            r->inputs_size + (*size),
            sizeof(PyObject *)
        );

        if (!merged)
            return -1;

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
        if (
            server_err(
                self,
                awaitable,
                500,
                r,
                NULL,
                method_str
            ) < 0
        )
            return -1;
    } else coro = PyObject_Vectorcall(
        r->callable,
        params,
        r->inputs_size,
        NULL
    );

    if (!coro)
        return -1;

    if (
        PyAwaitable_AddAwait(
            awaitable,
            coro,
            handle_route_callback,
            route_error
        ) < 0
    )
    {
        return -1;
    }

    return 0;
}

int
handle_route(PyObject *awaitable, char *query)
{
    PyObject *receive;
    route *r;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            NULL,
            NULL,
            &receive,
            NULL,
            NULL
        ) < 0
    )
        return -1;

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &r,
            NULL,
            NULL,
            NULL
        ) < 0
    )
        return -1;

    char *buf = PyMem_Malloc(INITIAL_BUF_SIZE);

    if (!buf)
    {
        PyErr_NoMemory();
        return -1;
    }

    Py_ssize_t *size = PyMem_Malloc(sizeof(Py_ssize_t));

    if (!size)
    {
        PyMem_Free(buf);
        PyErr_NoMemory();
        return -1;
    }

    Py_ssize_t *used = PyMem_Malloc(sizeof(Py_ssize_t));

    if (!used)
    {
        PyMem_Free(buf);
        PyMem_Free(used);
        PyErr_NoMemory();
        return -1;
    }

    *used = 0;
    *size = INITIAL_BUF_SIZE;
    strcpy(buf, "");

    PyObject *aw = PyAwaitable_New();
    if (!aw)
        return -1;

    if (
        PyAwaitable_SaveValues(
            aw,
            2,
            awaitable,
            receive
        ) < 0
    )
    {
        Py_DECREF(aw);
        PyMem_Free(buf);
        return -1;
    }


    if (
        PyAwaitable_SaveArbValues(
            aw,
            4,
            buf,
            size,
            used,
            query
        ) < 0
    )
    {
        Py_DECREF(aw);
        PyMem_Free(buf);
        return -1;
    }

    PyObject *receive_coro = PyObject_CallNoArgs(receive);

    if (!receive_coro)
    {
        Py_DECREF(aw);
        return -1;
    }

    if (
        PyAwaitable_AddAwait(
            aw,
            receive_coro,
            body_inc_buf,
            NULL
        ) < 0
    )
    {
        Py_DECREF(aw);
        PyMem_Free(buf);
        return -1;
    }

    Py_DECREF(receive_coro);

    if (
        PyAwaitable_AddAwait(
            awaitable,
            aw,
            NULL,
            NULL
        ) < 0
    )
    {
        Py_DECREF(aw);
        PyMem_Free(buf);
        return -1;
    }

    return 0;
}

int
handle_route_callback(
    PyObject *awaitable,
    PyObject *result
)
{
    ViewApp *self;
    PyObject *send;
    PyObject *scope;
    PyObject *receive;
    PyObject *raw_path;
    route *r;
    const char *method_str;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            &self,
            &scope,
            &receive,
            &send,
            &raw_path
        ) < 0
    )
        return -1;

    PyObject *view_result = PyObject_GetAttrString(
        result,
        "__view_result__"
    );
    if (view_result)
    {
        PyObject *context = context_from_data((PyObject *) self, scope);
        if (!context)
        {
            Py_DECREF(view_result);
            return -1;
        }

        result = PyObject_CallOneArg(view_result, context);
        Py_DECREF(view_result);
        if (!result)
            return -1;

        if (
            Py_TYPE(result)->tp_as_async && Py_TYPE(result)->tp_as_async->
            am_await
        )
        {
            // object is awaitable
            if (
                PyAwaitable_AddAwait(
                    awaitable,
                    result,
                    handle_route_callback,
                    route_error
                ) < 0
            )
            {
                Py_DECREF(result);
                return -1;
            }

            return 0;
        }
    } else Py_INCREF(result);

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &r,
            NULL,
            NULL,
            &method_str
        ) < 0
    )
    {
        Py_DECREF(result);
        return -1;
    }

    char *res_str;
    int status;
    PyObject *headers;

    if (
        handle_result(
            result,
            &res_str,
            &status,
            &headers,
            raw_path,
            method_str
        ) < 0
    )
    {
        Py_DECREF(result);
        return -1;
    }

    Py_DECREF(result);

    if (r->cache_rate > 0)
    {
        r->cache = res_str;
        r->cache_status = status;
        r->cache_headers = Py_NewRef(headers);
        r->cache_index = 0;
    }

    PyObject *dc = Py_BuildValue(
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

    PyObject *coro = PyObject_Vectorcall(
        send,
        (PyObject *[]) { dc },
        1,
        NULL
    );
    Py_DECREF(dc);

    if (!coro)
        return -1;

    if (
        PyAwaitable_AddAwait(
            awaitable,
            coro,
            NULL,
            NULL
        ) < 0
    )
    {
        Py_DECREF(coro);
        return -1;
    }
    ;

    Py_DECREF(coro);
    PyObject *dct = Py_BuildValue(
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
        (PyObject *[]) { dct },
        1,
        NULL
    );

    Py_DECREF(dct);
    if (r->cache_rate <= 0)
        PyMem_Free(res_str);
    if (!coro)
        return -1;

    if (
        PyAwaitable_AddAwait(
            awaitable,
            coro,
            NULL,
            NULL
        ) < 0
    )
    {
        Py_DECREF(coro);
        return -1;
    }

    Py_DECREF(coro);
    return 0;
}

int
send_raw_text(
    PyObject *awaitable,
    PyObject *send,
    int status,
    const char *res_str,
    PyObject *headers, /* may be NULL */
    bool is_http
)
{
    PyObject *coro;
    PyObject *send_dict;

    if (!headers)
    {
        send_dict = Py_BuildValue(
            "{s:s,s:i,s:[[y,y]]}",
            "type",
            is_http ? "http.response.start" : "websocket.http.response.start",
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
            (PyObject *[]) { send_dict },
            1,
            NULL
        );
    } else
    {
        send_dict = Py_BuildValue(
            "{s:s,s:i,s:O}",
            "type",
            is_http ? "http.response.start" : "websocket.http.response.start",
            "status",
            status,
            "headers",
            headers
        );

        if (!send_dict)
            return -1;

        coro = PyObject_Vectorcall(
            send,
            (PyObject *[]){send_dict},
            1,
            NULL
        );
    }
    Py_DECREF(send_dict);
    if (!coro)
        return -1;

    if (
        PyAwaitable_AddAwait(
            awaitable,
            coro,
            NULL,
            NULL
        ) < 0
    )
    {
        Py_DECREF(coro);
        return -1;
    }
    ;

    Py_DECREF(coro);
    PyObject *dict = Py_BuildValue(
        "{s:s,s:y}",
        "type",
        is_http ? "http.response.body" : "websocket.http.response.body",
        "body",
        res_str
    );

    if (!dict)
        return -1;

    coro = PyObject_Vectorcall(
        send,
        (PyObject *[]){dict},
        1,
        NULL
    );

    Py_DECREF(dict);

    if (!coro)
        return -1;

    if (
        PyAwaitable_AddAwait(
            awaitable,
            coro,
            NULL,
            NULL
        ) < 0
    )
    {
        Py_DECREF(coro);
        return -1;
    }

    Py_DECREF(coro);
    return 0;
}

int
handle_route_websocket(PyObject *awaitable, PyObject *result)
{
    char *res;
    int status = 1005;
    PyObject *headers;

    PyObject *send;
    PyObject *receive;
    PyObject *raw_path;
    route *r;
    const char *method_str;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            NULL,
            NULL,
            NULL,
            &send,
            &raw_path
        ) < 0
    ) return -1;

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &r,
            NULL,
            NULL,
            NULL
        ) < 0
    ) return -1;

    if (result == Py_None)
    {
        PyObject *args = Py_BuildValue(
            "(iOs)",
            1000,
            raw_path,
            "websocket_closed"
        );

        if (!args)
            return -1;

        if (
            !PyObject_Call(
                route_log,
                args,
                NULL
            )
        )
        {
            Py_DECREF(args);
            return -1;
        }
        Py_DECREF(args);
        return 0;
    }


    if (
        handle_result(
            result,
            &res,
            &status,
            &headers,
            raw_path,
            "websocket_closed"
        ) < 0
    )
        return -1;

    PyObject *send_dict = Py_BuildValue(
        "{s:s,s:s}",
        "type",
        "websocket.send",
        "text",
        res
    );
    free(res);

    if (!send_dict)
        return -1;

    PyObject *coro = PyObject_Vectorcall(
        send,
        (PyObject *[]) { send_dict },
        1,
        NULL
    );
    if (!coro)
    {
        Py_DECREF(send_dict);
        return -1;
    }

    Py_DECREF(send_dict);
    if (PyAwaitable_AddAwait(awaitable, coro, NULL, NULL) < 0)
    {
        Py_DECREF(coro);
        return -1;
    }
    return 0;
}
