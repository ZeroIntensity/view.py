/*
 * view.py route inputs implementation
 *
   // * This file is responsible for parsing route inputs through query
 * strings and body parameters.
 *
 * If a route has no inputs, then the parsing
 * step is skipped for optimization purposes.
 *
 * If a route has only query inputs, then we don't need to go through the
 * body parsing step, and only parse the query string (handle_route_query()).
 *
 * If a route has body inputs, then we start by parsing that, and if it has any
 * query string parameters, that's handled later. ASGI does not send the body
 * in a single receive() call, so we have a buffer that increases over time.
 *
 * This implementation is also in charge of building data inputs (such as Context() or WebSocket())
 * and appending them to routes. This is indicated by a special integer determined by the loader.
 *
 */
#include <Python.h>
#include <stdbool.h> // true

#include <view/app.h> // ViewApp
#include <view/context.h> // context_from_data
#include <view/errors.h>
#include <view/inputs.h> // app_parsers
#include <view/handling.h> // handle_route_impl
#include <view/typecodes.h>
#include <view/ws.h> // ws_from_data
#include <view/view.h> // VIEW_FATAL

#include <pyawaitable.h>

typedef struct _app_parsers app_parsers;
typedef PyObject **(* parserfunc)(
    app_parsers *,
    const char *,
    PyObject *,
    route_input **,
    Py_ssize_t
);

/*
 * PyAwaitable callback - do not call manually!
 *
 * This appends the internal buffer with the received body, and
 * calls itself as a coroutine until the entire body has been
 * received.
 *
 * After the body has been received, the route is sent to
 * the handler.
 */
int
body_inc_buf(PyObject *awaitable, PyObject *result)
{
    PyObject *body = PyDict_GetItemString(
        result,
        "body"
    );

    if (!body)
    {
        return PyErr_BadASGI();
    }

    PyObject *more_body = PyDict_GetItemString(
        result,
        "more_body"
    );
    if (!more_body)
    {
        return PyErr_BadASGI();
    }

    char *buf_inc;
    Py_ssize_t buf_inc_size;

    if (
        PyBytes_AsStringAndSize(
            body,
            &buf_inc,
            &buf_inc_size
        ) < 0
    )
    {
        return -1;
    }

    char *buf;
    Py_ssize_t *size;
    Py_ssize_t *used;
    char *query;

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &buf,
            &size,
            &used,
            &query
        ) < 0
    )
    {
        return -1;
    }

    char *nbuf = buf;
    bool needs_realloc = false;

    while (((*used) + buf_inc_size) > (*size))
    {
        // The buffer would overflow, we need to reallocate it
        *size *= 2;
        needs_realloc = true;
    }

    if (needs_realloc)
    {
        nbuf = PyMem_Realloc(
            buf,
            (*size)
        );

        if (!nbuf)
        {
            PyErr_NoMemory();
            return -1;
        }
    }

    strncat(
        nbuf,
        buf_inc,
        buf_inc_size
    );
    *used += buf_inc_size;
    PyAwaitable_SetArbValue(
        awaitable,
        0,
        nbuf
    );

    PyObject *aw;
    PyObject *receive;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            &aw,
            &receive
        ) < 0
    )
    {
        return -1;
    }

    if (PyObject_IsTrue(more_body))
    {
        PyObject *receive_coro = PyObject_CallNoArgs(receive);

        if (
            PyAwaitable_AddAwait(
                awaitable,
                receive_coro,
                body_inc_buf,
                NULL
            ) < 0
        )
        {
            Py_DECREF(receive_coro);
            PyMem_Free(query);
            PyMem_Free(nbuf);
            return -1;
        }

        Py_DECREF(receive_coro);
    } else
    {
        if (
            handle_route_impl(
                aw,
                nbuf,
                query
            ) < 0
        )
        {
            PyMem_Free(nbuf);
            return -1;
        }

        PyMem_Free(nbuf);
    }

    return 0;
}

/*
 * Call a route without parsing the body.
 */
int
handle_route_query(PyObject *awaitable, char *query)
{
    ViewApp *self;
    route *r;
    PyObject **path_params;
    Py_ssize_t *size;
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
        return -1;

    const char *method_str;

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            NULL,
            NULL,
            NULL,
            &method_str
        ) <
        0
    )
        return -1;

    PyObject *query_obj = query_parser(
        &self->parsers,
        query
    );

    if (!query_obj)
    {
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

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &r,
            &path_params,
            &size,
            NULL
        ) < 0
    )
    {
        Py_DECREF(query_obj);
        return -1;
    }

    Py_ssize_t fake_size = 0;

    if (size == NULL)
        size = &fake_size;
    PyObject **params = PyMem_Calloc(
        r->inputs_size,
        sizeof(PyObject *)
    );
    if (!params)
    {
        Py_DECREF(query_obj);
        return -1;
    }
    Py_ssize_t final_size = 0;

    for (int i = 0; i < r->inputs_size; i++)
    {
        if (r->inputs[i]->route_data)
        {
            PyObject *data = build_data_input(
                r->inputs[i]->route_data,
                (PyObject *) self,
                scope,
                receive,
                send
            );
            if (!data)
            {
                for (int i = 0; i < r->inputs_size; i++)
                    Py_XDECREF(params[i]);

                PyMem_Free(params);
                Py_DECREF(query_obj);
                return -1;
            }

            params[i] = data;
            ++final_size;
            continue;
        }

        PyObject *item = PyDict_GetItemString(
            query_obj,
            r->inputs[i]->name
        );

        if (!item)
        {
            if (r->inputs[i]->df)
            {
                params[i] = r->inputs[i]->df;
                ++final_size;
                continue;
            }

            for (int i = 0; i < r->inputs_size; i++)
                Py_XDECREF(params[i]);

            PyMem_Free(params);
            Py_DECREF(query_obj);
            return fire_error(
                self,
                awaitable,
                400,
                r,
                NULL,
                NULL,
                method_str,
                r->is_http
            );
        } else ++final_size;

        if (item)
        {
            PyObject *parsed_item = cast_from_typecodes(
                r->inputs[i]->types,
                r->inputs[i]->types_size,
                item,
                self->parsers.json,
                true
            );
            if (!parsed_item)
            {
                PyErr_Clear();
                for (int i = 0; i < r->inputs_size; i++)
                    Py_XDECREF(params[i]);

                PyMem_Free(params);
                Py_DECREF(query_obj);
                return fire_error(
                    self,
                    awaitable,
                    400,
                    r,
                    NULL,
                    NULL,
                    method_str,
                    r->is_http
                );
            }
            params[i] = parsed_item;
        }
    }

    PyObject **merged = PyMem_Calloc(
        final_size + (*size),
        sizeof(PyObject *)
    );

    if (!merged)
    {
        PyErr_NoMemory();
        return -1;
    }

    for (int i = 0; i < (*size); i++)
        merged[i] = path_params[i];

    for (int i = 0; i < final_size; i++)
        merged[*size + i] = params[i];

    PyObject *coro = PyObject_Vectorcall(
        r->callable,
        merged,
        *size + final_size,
        NULL
    );

    for (int i = 0; i < final_size + *size; i++)
        Py_XDECREF(merged[i]);

    PyMem_Free(merged);
    PyMem_Free(params);
    Py_DECREF(query_obj);

    if (!coro)
        return -1;

    if (
        PyAwaitable_AddAwait(
            awaitable,
            coro,
            r->is_http ? handle_route_callback : handle_route_websocket,
            route_error
        ) < 0
    )
    {
        Py_DECREF(coro);
        return -1;
    }

    Py_DECREF(coro);
    return 0;
}

/*
 * Parse a query string into a Python dictionary.
 */
PyObject *
query_parser(
    app_parsers *parsers,
    const char *data
)
{
    PyObject *py_str = PyUnicode_FromString(data);

    if (!py_str)
        return NULL;

    PyObject *obj = PyObject_Vectorcall(
        parsers->query,
        (PyObject *[]) { py_str },
        1,
        NULL
    );

    Py_DECREF(py_str);
    return obj; // no need for null check
}

/*
 * Build a route data object based on the given data ID (determined by the loader).
 *
 * As of now:
 * - 1: Context()
 * - 2: WebSocket(), only supported on WebSocket routes
 */
PyObject *
build_data_input(
    int num,
    PyObject *app,
    PyObject *scope,
    PyObject *receive,
    PyObject *send
)
{
    switch (num)
    {
    case 1:
        return context_from_data(app, scope);
    case 2:
        return ws_from_data(
            scope,
            send,
            receive
        );

    default:
        VIEW_FATAL("got invalid route data number");
    }
    return NULL; // to make editor happy
}

static PyObject *
parse_body(
    const char *data,
    app_parsers *parsers,
    PyObject *scope
)
{
    PyObject *py_str = PyUnicode_FromString(data);
    if (!py_str)
        return NULL;

    PyObject *obj = PyObject_Vectorcall(
        parsers->json,
        (PyObject *[]) { py_str },
        1,
        NULL
    );
    Py_DECREF(py_str);

    return obj;
}

PyObject **
generate_params(
    ViewApp *app,
    app_parsers *parsers,
    const char *data,
    PyObject *query,
    route_input **inputs,
    Py_ssize_t inputs_size,
    PyObject *scope,
    PyObject *receive,
    PyObject *send
)
{
    PyObject *obj = parse_body(data, parsers, scope);
    if (!obj)
    {
        return NULL;
    }

    PyObject **ob = PyMem_Calloc(
        inputs_size,
        sizeof(PyObject *)
    );

    if (!ob)
    {
        PyErr_NoMemory();
        Py_DECREF(obj);
        return NULL;
    }

    for (int i = 0; i < inputs_size; i++)
    {
        route_input *inp = inputs[i];
        if (inp->route_data)
        {
            PyObject *data = build_data_input(
                inp->route_data,
                (PyObject *) app,
                scope,
                receive,
                send
            );
            if (!data)
            {
                Py_DECREF(obj);
                PyMem_Free(ob);
                return NULL;
            }

            ob[i] = data;
            continue;
        }

        // Borrowed reference
        PyObject *raw_item = PyDict_GetItemString(
            inp->is_body ? obj : query,
            inp->name
        );
        PyObject *item = cast_from_typecodes(
            inp->types,
            inp->types_size,
            raw_item,
            parsers->json,
            true
        );

        if (!item)
        {
            assert(PyErr_Occurred());
            Py_DECREF(obj);
            PyMem_Free(ob);
            return NULL;
        }

        for (int x = 0; x < inp->validators_size; x++)
        {
            PyObject *o = PyObject_Vectorcall(
                inp->validators[x],
                (PyObject *[]) { item },
                1,
                NULL
            );
            if (!PyObject_IsTrue(o))
            {
                Py_DECREF(o);
                PyMem_Free(ob);
                Py_DECREF(obj);
                Py_DECREF(item);
                return NULL;
            }
        }

        ob[i] = item;
    }

    Py_DECREF(obj);
    return ob;
}
