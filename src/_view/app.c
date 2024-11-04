/*
 * view.py ASGI app implementation
 *
 * This file contains the ViewApp class, which is the base class for the App class.
 * All the actual ASGI calls are here. The ASGI app location is under the asgi_app_entry() method.
 *
 * The view.py ASGI app should *never* raise an exception (in a perfect world, at least). All errors
 * should be handled accordingly, and a proper HTTP response should be sent back in all cases, regardless of what happened.
 *
 * The lifecycle of a request is as follows:
 *
 * - Receive ASGI values (scope, receive(), and send())
 * - If it's a lifespan call, start the lifespan protocol.
 * - If not, extract the path and method from the scope.
 * - If it's an HTTP request:
 *       * Search the corresponding method map with the route.
 *       * If it's not found, check if the app has path parameters.
 *           > If not, return a 404.
 *           > If it does, defer to the path parts API (very unstable and buggy).
 *       * If it is found, check if the route has inputs (data inputs, query parameters, and body parameters).
 *           > If it does, defer to the proper handler function.
 *           > If not, we can just call it right now, and send the result to the results API.
 * - If it's a WebSocket connection:
 *       * Search the WebSocket map with the route.
 *       * If it's not found, check if the app has path parameters.
 *           > If not, return a 404, but explicitly mark it as a WebSocket rejection (websocket.http.response)
 *           > If it does, defer to the path parts API (very unstable and buggy). This is not implemented yet!
 *       * Defer to the proper handler function. A WebSocket route always has at least one input.
 */
#include <Python.h>

#include <stdbool.h>
#include <signal.h>

#include <view/app.h>
#include <view/backport.h>
#include <view/errors.h>
#include <view/parts.h> // extract_parts, load_parts
#include <view/results.h> // pymem_strdup
#include <view/handling.h> // route_free, route_new, handle_route, handle_route_query
#include <view/map.h>
#include <view/view.h> // VIEW_FATAL

#include <pyawaitable.h>

#define LOAD_ROUTE(target)                                                  \
        char *path;                                                         \
        PyObject *callable;                                                 \
        PyObject *inputs;                                                   \
        Py_ssize_t cache_rate;                                              \
        PyObject *errors;                                                   \
        PyObject *parts = NULL;                                             \
        if (!PyArg_ParseTuple(                                              \
    args,                                                                   \
    "zOnOOO",                                                               \
    &path,                                                                  \
    &callable,                                                              \
    &cache_rate,                                                            \
    &inputs,                                                                \
    &errors,                                                                \
    &parts                                                                  \
            )) return NULL;                                                 \
        route *r = route_new(                                               \
    callable,                                                               \
    PySequence_Size(inputs),                                                \
    cache_rate,                                                             \
    figure_has_body(inputs)                                                 \
                   );                                                       \
        if (!r) return NULL;                                                \
        if (load_typecodes(                                                 \
    r,                                                                      \
    inputs                                                                  \
            ) < 0) {                                                        \
            route_free(r);                                                  \
            return NULL;                                                    \
        }                                                                   \
        if (load_errors(r, errors) < 0) {                                   \
            route_free(r);                                                  \
            return NULL;                                                    \
        }                                                                   \
        if (!map_get(self->all_routes, path)) {                             \
            int *num = PyMem_Malloc(sizeof(int));                           \
            if (!num) {                                                     \
                PyErr_NoMemory();                                           \
                route_free(r);                                              \
                return NULL;                                                \
            }                                                               \
            *num = 1;                                                       \
            map_set(self->all_routes, path, num);                           \
        }                                                                   \
        if (!PySequence_Size(parts))                                        \
        map_set(self->target, path, r);                                     \
        else if (load_parts(self, self->target, parts, r) < 0) return NULL; \

#define ROUTE(target)             \
        static PyObject *target ( \
    ViewApp * self,               \
    PyObject * args               \
        ) {                       \
            LOAD_ROUTE(target);   \
            Py_RETURN_NONE;       \
        }

/*
 * Something unexpected happened with the received ASGI data (e.g. the scope is missing a key).
 * Don't call this manually, use the PyErr_BadASGI macro, which passes the file and lineno.
 */
COLD int
view_PyErr_BadASGI(char *file, int lineno)
{
    PyErr_Format(
        PyExc_RuntimeError,
        "(%s:%d) problem with view.py's ASGI server (this is a bug!)",
        file,
        lineno
    );
    return -1;
}

/*
 * Allocate and initialize a new ViewApp object.
 * This builds all the route tables, and any other field on the ViewApp struct.
 */
static PyObject *
new(PyTypeObject *tp, PyObject *args, PyObject *kwds)
{
    ViewApp *self = (ViewApp *) tp->tp_alloc(
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

    if (
        !self->options || !self->patch || !self->delete ||
        !self->post ||
        !self->put || !self->put || !self->get
    )
    {
        // TODO: Fix these leaks!
        // However, this is an unlikely case that will only happen
        // if the interpreter is out of memory.
        return NULL;
    }
    ;

    for (int i = 0; i < 28; i++)
        self->client_errors[i] = NULL;

    for (int i = 0; i < 11; i++)
        self->server_errors[i] = NULL;

    self->has_path_params = false;
    self->error_type = NULL;

    return (PyObject *) self;
}

/*
 * Dummy function to stop manual construction of a ViewApp from Python.
 * In a perfect world, this will never get called.
 */
static int
init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyErr_SetString(
        PyExc_TypeError,
        "ViewApp is not constructable"
    );
    return -1;
}

/*
 * ASGI lifespan implementation.
 */
static int
lifespan(PyObject *awaitable, PyObject *result)
{
    // This needs to be here, or else the server will complain about lifespan not being supported.
    // Most of this is undocumented and unavailable for use from the user for now.
    ViewApp *self;
    PyObject *send;
    PyObject *receive;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            &self,
            NULL,
            &receive,
            &send
        ) < 0
    )
        return -1;

    // Borrowed reference - do not DECREF
    PyObject *tp = PyDict_GetItemString(
        result,
        "type"
    );
    if (tp == NULL)
        return PyErr_BadASGI();
    const char *type = PyUnicode_AsUTF8(tp);

    bool is_startup = !strcmp(
        type,
        "lifespan.startup"
    );
    PyObject *target_obj = is_startup ? self->startup : self->cleanup;
    if (target_obj)
    {
        if (!PyObject_CallNoArgs(target_obj))
            return -1;
    }

    PyObject *send_dict = Py_BuildValue(
        "{s:s}",
        "type",
        is_startup ? "lifespan.startup.complete" :
        "lifespan.shutdown.complete"
    );

    if (!send_dict)
        return -1;

    PyObject *send_coro = PyObject_Vectorcall(
        send,
        (PyObject *[]) { send_dict },
        1,
        NULL
    );

    if (!send_coro)
        return -1;

    Py_DECREF(send_dict);

    if (
        PyAwaitable_AddAwait(
            awaitable,
            send_coro,
            NULL,
            NULL
        ) < 0
    )
    {
        Py_DECREF(send_coro);
        return -1;
    }
    Py_DECREF(send_coro);
    if (!is_startup) return 0;

    PyObject *aw = PyAwaitable_New();
    if (!aw)
        return -1;

    PyObject *recv_coro = PyObject_CallNoArgs(receive);
    if (!recv_coro)
    {
        Py_DECREF(aw);
        return -1;
    }

    if (
        PyAwaitable_AddAwait(
            aw,
            recv_coro,
            lifespan,
            NULL
        ) < 0
    )
    {
        Py_DECREF(aw);
        Py_DECREF(recv_coro);
        return -1;
    }
    ;

    return 0;
}

/* The ViewApp deallocator. */
static void
dealloc(ViewApp *self)
{
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

/*
 * Utility function for getting a key from the ASGI scope.
 * If the key is missing, an error is thown via PyErr_BadASGI().
 */
static const char *
dict_get_str(PyObject *dict, const char *str)
{
    Py_INCREF(dict);
    PyObject *ob = PyDict_GetItemString(
        dict,
        str
    );
    Py_DECREF(dict);
    if (!ob)
    {
        PyErr_BadASGI();
        return NULL;
    }

    const char *result = PyUnicode_AsUTF8(ob);
    return result;
}

/*
 * view.py ASGI implementation. This is where the magic happens!
 *
 * This is accessible via asgi_app_entry() in Python.
 *
 */
HOT static PyObject *
app(
    ViewApp *self,
    PyObject * const *args,
    Py_ssize_t nargs
)
{
    /*
     * All HTTP and WebSocket connections start here. This function is responsible for
     * looking up loaded routes, calling PyAwaitable, and so on.
     *
     * Note that a lot of things aren't actually implemented here, such as route handling, but
     * it's all sort of stitched together in this function.
     *
     * As mentioned in the top comment, this should always send some sort
     * of response back to the user, regardless of how badly things went.
     *
     * For example, if an error occurred somewhere, this should sent
     * back a 500 (assuming that an exception handler doesn't exist).
     *
     * We don't want to let the ASGI server do it, because then we're
     * missing out on the chance to call an error handler or log what happened.
     */

    // We can assume that there will be three arguments.
    // If there aren't, then something is seriously wrong!
    assert(nargs == 3);
    PyObject *scope = args[0];
    PyObject *receive = args[1];
    PyObject *send = args[2];

    // Borrowed reference
    PyObject *tp = PyDict_GetItemString(
        scope,
        "type"
    );

    if (!tp)
    {
        PyErr_BadASGI();
        return NULL;
    }

    const char *type = PyUnicode_AsUTF8(tp);

    PyObject *awaitable = PyAwaitable_New();
    if (!awaitable)
        return NULL;

    if (
        !strcmp(
            type,
            "lifespan"
        )
    )
    {
        // We are in the lifespan protocol!
        PyObject *recv_coro = PyObject_CallNoArgs(receive);
        if (!recv_coro)
        {
            Py_DECREF(awaitable);
            return NULL;
        }

        if (
            PyAwaitable_SaveValues(
                awaitable,
                4,
                self,
                scope,
                receive,
                send
            ) < 0
        )
        {
            Py_DECREF(awaitable);
            return NULL;
        }

        if (
            PyAwaitable_AddAwait(
                awaitable,
                recv_coro,
                lifespan,
                NULL
            ) < 0
        )
        {
            Py_DECREF(awaitable);
            Py_DECREF(recv_coro);
            return NULL;
        }
        ;
        Py_DECREF(recv_coro);
        return awaitable;
    }

    PyObject *raw_path_obj = PyDict_GetItemString(
        scope,
        "path"
    );

    if (!raw_path_obj)
    {
        Py_DECREF(awaitable);
        PyErr_BadASGI();
        return NULL;
    }

    const char *raw_path = PyUnicode_AsUTF8(raw_path_obj);
    if (!raw_path)
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (
        PyAwaitable_SaveValues(
            awaitable,
            5,
            self,
            scope,
            receive,
            send,
            raw_path_obj
        ) < 0
    )
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    bool is_http = !strcmp(
        type,
        "http"
    );

    size_t len = strlen(raw_path);
    char *path;
    if (raw_path[len - 1] == '/' && len != 1)
    {
        path = PyMem_Malloc(len + 1);
        if (!path)
        {
            Py_DECREF(awaitable);
            return PyErr_NoMemory();
        }

        memcpy(path, raw_path, len);
        path[len - 1] = '\0';
    } else
    {
        path = pymem_strdup(raw_path, len);
        if (!path)
        {
            Py_DECREF(awaitable);
            return PyErr_NoMemory();
        }
    }
    const char *method = NULL;

    if (is_http)
    {
        method = dict_get_str(
            scope,
            "method"
        );
    }

    PyObject *query_obj = PyDict_GetItemString(
        scope,
        "query_string"
    );

    if (!query_obj)
    {
        Py_DECREF(awaitable);
        PyMem_Free(path);
        return NULL;
    }

    Py_ssize_t query_size;
    char *query_str;

    if (PyBytes_AsStringAndSize(query_obj, &query_str, &query_size) < 0)
    {
        Py_DECREF(awaitable);
        PyMem_Free(path);
        return NULL;
    }
    char *query = pymem_strdup(query_str, query_size);
    map *ptr = self->websocket; // ws by default
    const char *method_str = "websocket";

    if (is_http)
    {
        if (
            !strcmp(
                method,
                "GET"
            )
        )
        {
            ptr = self->get;
            method_str = "GET";
        } else if (
            !strcmp(
                method,
                "POST"
            )
        )
        {
            ptr = self->post;
            method_str = "POST";
        } else if (
            !strcmp(
                method,
                "PATCH"
            )
        )
        {
            ptr = self->patch;
            method_str = "PATCH";
        } else if (
            !strcmp(
                method,
                "PUT"
            )
        )
        {
            ptr = self->put;
            method_str = "PUT";
        } else if (
            !strcmp(
                method,
                "DELETE"
            )
        )
        {
            ptr = self->delete;
            method_str = "DELETE";
        } else if (
            !strcmp(
                method,
                "OPTIONS"
            )
        )
        {
            ptr = self->options;
            method_str = "OPTIONS";
        }
        if (ptr == self->websocket)
        {
            ptr = self->get;
        }
    }

    route *r = map_get(
        ptr,
        path
    );
    PyObject **params = NULL;
    Py_ssize_t *size = NULL;

    if (!r || r->r)
    {
        if (!self->has_path_params)
        {
            if (
                map_get(
                    self->all_routes,
                    path
                )
            )
            {
                if (
                    fire_error(
                        self,
                        awaitable,
                        405,
                        NULL,
                        NULL,
                        NULL,
                        method_str,
                        is_http
                    ) < 0
                )
                {
                    Py_DECREF(awaitable);
                    PyMem_Free(path);
                    return NULL;
                }
                PyMem_Free(path);
                return awaitable;
            }
            if (
                fire_error(
                    self,
                    awaitable,
                    404,
                    NULL,
                    NULL,
                    NULL,
                    method_str,
                    is_http
                ) < 0
            )
            {
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
        if (res < 0)
        {
            PyMem_Free(path);
            PyMem_Free(size);

            if (res == -1)
            {
                // -1 denotes that an exception occurred, raise it
                Py_DECREF(awaitable);
                return NULL;
            }

            // -2 denotes that an error can be sent to the client, return
            // the awaitable for execution of send()
            return awaitable;
        }
    }

    if (
        is_http && (r->cache_rate != -1) && (r->cache_index++ <
                                             r->cache_rate) &&
        r->cache
    )
    {
        // We have a cached response that we can use!
        // Let's start the ASGI response process
        PyObject *dct = Py_BuildValue(
            "{s:s,s:i,s:O}",
            "type",
            "http.response.start",
            "status",
            r->cache_status,
            "headers",
            r->cache_headers
        );

        if (!dct)
        {
            if (size)
            {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                PyMem_Free(params);
                PyMem_Free(size);
            }
            PyMem_Free(path);
            Py_DECREF(awaitable);
            return NULL;
        }

        PyObject *coro = PyObject_Vectorcall(
            send,
            (PyObject *[]) { dct },
            1,
            NULL
        );

        Py_DECREF(dct);

        if (!coro)
        {
            if (size)
            {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                PyMem_Free(params);
                PyMem_Free(size);
            }
            PyMem_Free(path);
            Py_DECREF(awaitable);
            return NULL;
        }

        if (
            PyAwaitable_AddAwait(
                awaitable,
                coro,
                NULL,
                NULL
            ) < 0
        )
        {
            if (size)
            {
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

        PyObject *dc = Py_BuildValue(
            "{s:s,s:y}",
            "type",
            "http.response.body",
            "body",
            r->cache
        );

        if (!dc)
        {
            if (size)
            {
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
            (PyObject *[]) { dc },
            1,
            NULL
        );

        Py_DECREF(dc);

        if (!coro)
        {
            if (size)
            {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                PyMem_Free(params);
                PyMem_Free(size);
            }
            Py_DECREF(awaitable);
            PyMem_Free(path);
            return NULL;
        }

        if (
            PyAwaitable_AddAwait(
                awaitable,
                coro,
                NULL,
                NULL
            ) < 0
        )
        {
            if (size)
            {
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

    if (
        PyAwaitable_SaveArbValues(
            awaitable,
            4,
            r,
            params,
            size,
            method_str
        ) < 0
    )
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (PyAwaitable_SaveIntValues(awaitable, 1, is_http) < 0)
    {
        Py_DECREF(awaitable);
        return NULL;
    }

    if (r->inputs_size != 0)
    {
        if (!r->has_body)
        {
            if (
                handle_route_query(
                    awaitable,
                    query
                ) < 0
            )
            {
                Py_DECREF(awaitable);
                PyMem_Free(path);
                return NULL;
            }
            ;

            return awaitable;
        }

        if (
            handle_route(
                awaitable,
                query
            ) < 0
        )
        {
            Py_DECREF(awaitable);
            return NULL;
        }

        return awaitable;
    } else
    {
        PyErr_SetString(PyExc_RuntimeError, "not right now");
        return NULL;
        // If there are no inputs, we can skip parsing!
        if (!is_http) VIEW_FATAL("got a websocket without an input!");

        PyObject *res_coro;
        if (size)
        {
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

        if (!res_coro)
        {
            Py_DECREF(awaitable);
            PyMem_Free(path);
            return NULL;
        }

        if (!res_coro)
        {
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
                return NULL;
            return awaitable;
        }
        if (
            PyAwaitable_AddAwait(
                awaitable,
                res_coro,
                handle_route_callback,
                route_error
            ) < 0
        )
        {
            Py_DECREF(res_coro);
            PyMem_Free(path);
            Py_DECREF(awaitable);
            return NULL;
        }
    }

    return awaitable;
}

/*
 * These are all loader functions that allocate a route structure and store
 * it on the corresponding route table.
 */
ROUTE(get);
ROUTE(post);
ROUTE(patch);
ROUTE(put);
ROUTE(delete);
ROUTE(options);

/*
 * Loader function for WebSockets.
 * We have a special case for WebSocket routes - the `is_http` field is set to false.
 */
static PyObject *
websocket(ViewApp *self, PyObject *args)
{
    LOAD_ROUTE(websocket);
    r->is_http = false;
    Py_RETURN_NONE;
}

/*
 * Adds a global error handler to the app.
 *
 * Note that this is for *status* codes only, not exceptions!
 * For example, if a route returned 400 without raising an exception,
 * then the handler for error 400 would be called.
 *
 * This is more or less undocumented, and subject to change.
 */
static PyObject *
err_handler(ViewApp *self, PyObject *args)
{
    PyObject *handler;
    int status_code;

    if (
        !PyArg_ParseTuple(
            args,
            "iO",
            &status_code,
            &handler
        )
    ) return NULL;

    if (status_code < 400 || status_code > 511)
    {
        PyErr_Format(
            PyExc_ValueError,
            "%d is not a valid status code",
            status_code
        );
        return NULL;
    }

    if (status_code >= 500)
    {
        self->server_errors[status_code - 500] = Py_NewRef(handler);
    } else
    {
        uint16_t index = hash_client_error(status_code);
        if (index == 600)
        {
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

/*
 * Adds a global exception handler to the app.
 *
 * This is similar to err_handler(), but this
 * catches exceptions instead of error response codes.
 */
static PyObject *
exc_handler(ViewApp *self, PyObject *args)
{
    PyObject *dict;
    if (
        !PyArg_ParseTuple(
            args,
            "O!",
            &PyDict_Type,
            &dict
        )
    ) return NULL;
    if (self->exceptions)
    {
        PyDict_Merge(
            self->exceptions,
            dict,
            1
        );
    } else
    {
        self->exceptions = Py_NewRef(dict);
    }

    Py_RETURN_NONE;
}

/*
 * Simple function that defers a
 * segmentation fault to the VIEW_FATAL macro.
 *
 * This is only active as a signal handler
 * when development mode is enabled.
 */
static void
sigsegv_handler(int signum)
{
    signal(
        SIGSEGV,
        SIG_DFL
    );
    VIEW_FATAL("segmentation fault");
}

/*
 * Set whether the app is in development mode.
 *
 * If it is, then the SIGSEGV handler is enabled.
 */
static PyObject *
set_dev_state(ViewApp *self, PyObject *args)
{
    int value;
    if (
        !PyArg_ParseTuple(
            args,
            "p",
            &value
        )
    ) return NULL;
    self->dev = (bool) value;

    if (value)
        signal(
            SIGSEGV,
            sigsegv_handler
        );

    Py_RETURN_NONE;
}

/*
 * Supply Python parser functions to C code.
 *
 * As of now, this only takes a query string parser and a JSON parser, but
 * that is pretty much gaurunteed to change.
 */
static PyObject *
supply_parsers(ViewApp *self, PyObject *args)
{
    PyObject *query;
    PyObject *json;

    if (
        !PyArg_ParseTuple(
            args,
            "OO",
            &query,
            &json
        )
    )
        return NULL;

    self->parsers.query = query;
    self->parsers.json = json;
    Py_RETURN_NONE;
}

/*
 * Register the base class to be recognized as an HTTP error.
 */
static PyObject *
register_error(ViewApp *self, PyObject *args)
{
    PyObject *type;

    if (
        !PyArg_ParseTuple(
            args,
            "O",
            &type
        )
    )
        return NULL;

    if (Py_TYPE(type) != &PyType_Type)
    {
        PyErr_SetString(
            PyExc_RuntimeError,
            "_register_error got an object that is not a type"
        );
        return NULL;
    }

    self->error_type = Py_NewRef(type);
    Py_RETURN_NONE;
}

static PyMethodDef methods[] =
{
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

PyTypeObject ViewAppType =
{
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
