#include <Python.h>

#include <stdint.h>  // uint16_t
#include <stdbool.h> // bool

#include <view/app.h> // ViewApp
#include <view/backport.h>
#include <view/errors.h>
#include <view/handling.h> // send_raw_text
#include <view/results.h> // handle_result
#include <view/route.h> // route
#include <view/view.h> // invalid_status_error

#include <pyawaitable.h>

#define ER(code, str) \
        case code:    \
            return str
#define ERR(code, msg)            \
        case code:                \
            return send_raw_text( \
    awaitable,                    \
    send,                         \
    code,                         \
    msg,                          \
    true                          \
            );

/*
 * Print an error without clearing it.
 */
void
show_error(bool dev)
{
    if (dev)
    {
        PyObject *err = PyErr_GetRaisedException();
        Py_INCREF(err); // Save a reference to it
        PyErr_SetRaisedException(err);
        PyErr_Print();
        // PyErr_Print() clears the error indicator, so
        // we need to reset it.
        PyErr_SetRaisedException(err);
    } else PyErr_Clear();
}

/*
 * Mappings between error codes and their index.
 * 400 - 0
 * 401 - 1
 * 402 - 2
 * 403 - 3
 * 404 - 4
 * 405 - 5
 * 406 - 6
 * 407 - 7
 * 408 - 8
 * 409 - 9
 * 410 - 10
 * 411 - 11
 * 412 - 12
 * 413 - 13
 * 414 - 14
 * 415 - 15
 * 416 - 16
 * 417 - 17
 * 418 - 18
 * NOTICE: status codes start to skip around now!
 * 421 - 19
 * 422 - 20
 * 423 - 21
 * 424 - 22
 * 425 - 23
 * 426 - 24
 * 428 - 25
 * 429 - 26
 * 431 - 27
 * 451 - 28
 */

/*
 * Translate the error code into an index for the error table.
 * See above for the mappings between status codes and indicies.
 */
uint16_t
hash_client_error(int status)
{
    if (status < 419)
    {
        return status - 400;
    }

    if (status < 427)
    {
        return status - 402;
    }

    if (status < 430)
    {
        return status - 406;
    }

    if (status == 431)
    {
        return 27;
    }

    if (status == 451)
    {
        return 28;
    }

    PyErr_Format(
        invalid_status_error,
        "%d is not a valid status code",
        status
    );
    return 600;
}

/*
 * Translate a server error into an index for the error table.
 */
uint16_t
hash_server_error(int status)
{
    uint16_t index = status - (status < 509 ? 500 : 501);
    if ((index < 0) || (index > 10))
    {
        PyErr_Format(
            invalid_status_error,
            "%d is not a valid status code",
            status
        );
        return 600;
    }
    return index;
}

/*
 * Get the stringified version of an error (e.g. 400 -> "Bad Request").
 * These strings are static, and do not need to be freed by the caller.
 */
static const char *
get_err_str(int status)
{
    switch (status)
    {
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

/*
 * PyAwaitable callback for an error handler.
 *
 * This function takes the result of an error callback, which is
 * the same as any route callback, so the result is deferred to handle_result()
 */
static int
finalize_err_cb(PyObject *awaitable, PyObject *result)
{
    PyObject *send;
    PyObject *raw_path;
    const char *method_str;
    route *r;
    int is_http;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            &send,
            &raw_path
        ) < 0
    )
        return -1;

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &r,
            &method_str
        ) < 0
    )
        return -1;

    if (PyAwaitable_UnpackIntValues(awaitable, &is_http) < 0)
        return -1;

    char *res_str;
    int status_code;
    PyObject *headers;

    if (
        handle_result(
            result,
            &res_str,
            &status_code,
            &headers,
            raw_path,
            method_str
        ) < 0
    )
    {
        Py_DECREF(result);
        return -1;
    }

    if (
        send_raw_text(
            awaitable,
            send,
            status_code,
            res_str,
            headers,
            is_http
        ) < 0
    )
    {
        Py_DECREF(result);
        PyMem_Free(res_str);
        return -1;
    }

    PyMem_Free(res_str);
    return 0;
}

static int
run_err_cb(
    PyObject *awaitable,
    PyObject *handler,
    PyObject *send,
    int status,
    bool *called,
    const char *message,
    route *r,
    PyObject *raw_path,
    const char *method,
    bool is_http
)
{
    if (!handler)
    {
        if (called)
            *called = false;
        const char *msg;
        if (!message)
        {
            msg = get_err_str(status);
            if (!msg)
                return -1;
        } else
            msg = message;

        PyObject *args = Py_BuildValue(
            "(iOs)",
            status,
            raw_path,
            method
        );

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
        if (
            send_raw_text(
                awaitable,
                send,
                status,
                msg,
                NULL,
                is_http
            ) < 0
        )
            return -1;

        return 0;
    }
    if (called)
        *called = true;

    PyObject *coro = PyObject_CallNoArgs(handler);

    if (!coro)
        return -1;

    PyObject *new_awaitable = PyAwaitable_New();

    if (!new_awaitable)
    {
        Py_DECREF(coro);
        return -1;
    }

    if (
        PyAwaitable_SaveValues(
            new_awaitable,
            2,
            send,
            raw_path
        ) < 0
    )
    {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    if (
        PyAwaitable_SaveArbValues(
            new_awaitable,
            1,
            r
        ) < 0
    )
    {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    if (PyAwaitable_SaveIntValues(new_awaitable, 1, is_http) < 0)
    {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    if (
        PyAwaitable_AddAwait(
            new_awaitable,
            coro,
            finalize_err_cb,
            NULL
        ) < 0
    )
    {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    if (
        PyAwaitable_AddAwait(
            awaitable,
            new_awaitable,
            NULL,
            NULL
        ) < 0
    )
    {
        Py_DECREF(new_awaitable);
        Py_DECREF(coro);
        return -1;
    }

    return 0;
}

int
fire_error(
    ViewApp *self,
    PyObject *awaitable,
    int status,
    route *r,
    bool *called,
    const char *message,
    const char *method_str,
    bool is_http
)
{
    PyObject *send;
    PyObject *raw_path;

    if (
        PyAwaitable_UnpackValues(
            awaitable,
            NULL,
            NULL,
            NULL,
            &send,
            &raw_path
        ) < 0
    )
        return -1;

    uint16_t index = 0;
    PyObject *handler = NULL;

    if (status >= 500)
    {
        index = hash_server_error(status);
        if (index == 600)
        {
            return -1;
        }
        if (r)
            handler = r->server_errors[index];
        if (!handler)
            handler = self->server_errors[index];
    } else
    {
        index = hash_client_error(status);
        if (index == 600)
        {
            return -1;
        }
        if (r)
            handler = r->client_errors[index];
        if (!handler)
            handler = self->client_errors[index];
    }

    if (
        run_err_cb(
            awaitable,
            handler,
            send,
            status,
            called,
            message,
            r,
            raw_path,
            method_str,
            is_http
        ) < 0
    )
    {
        if (
            send_raw_text(
                awaitable,
                send,
                500,
                "failed to dispatch error handler",
                NULL,
                is_http
            ) < 0
        )
        {
            return -1;
        }
    }

    return 0;
}

static int
server_err_exc(
    ViewApp *self,
    PyObject *awaitable,
    uint16_t status,
    route *r,
    bool *handler_was_called,
    PyObject *msg,
    const char *method_str
)
{
    const char *message = NULL;
    PyObject *msg_str = NULL;
    PyErr_Clear();

    if (self->dev)
    {
        assert(msg != NULL);
        msg_str = PyObject_Str(msg);
        if (!msg_str)
        {
            return -1;
        }

        message = PyUnicode_AsUTF8(msg_str);
        if (!message)
        {
            Py_DECREF(msg_str);
            return -1;
        }
    }

    if (
        fire_error(
            self,
            awaitable,
            status,
            r,
            handler_was_called,
            message,
            method_str,
            true
        ) < 0
    )
    {
        Py_XDECREF(msg_str);
        return -1;
    }

    Py_XDECREF(msg_str);
    return 0;
}

int
server_err(
    ViewApp *self,
    PyObject *awaitable,
    uint16_t status,
    route *r,
    bool *handler_was_called,
    const char *method_str
)
{
    int res = server_err_exc(
        self,
        awaitable,
        status,
        r,
        handler_was_called,
        PyErr_GetRaisedException(),
        method_str
    );
    return res;
}

int
route_error(
    PyObject *awaitable,
    PyObject *err
)
{
<<<<<<< HEAD
    if (PyErr_GivenExceptionMatches(err, ws_disconnect_err))
=======
    puts("1");
    if (((PyObject *) Py_TYPE(err)) == ws_disconnect_err)
>>>>>>> b9b43de5bfda018d39bedd5d278e1e1db3c8bf58
    {
        // the socket prematurely disconnected, let's complain about it
        #if PY_MINOR_VERSION < 9
        PyObject *args = Py_BuildValue(
            "(s)",
            "Unhandled WebSocket disconnect"
        );
        if (!args)
            return -2;

        if (!PyObject_Call(route_warn, args, NULL))
        {
            Py_DECREF(args);
            return -2;
        }
        #else
        PyObject *message = PyUnicode_FromStringAndSize(
            "Unhandled WebSocket disconnect",
            sizeof(
                "Unhandled WebSocket disconnect") - 1
        );
        if (!message)
            return -2;

        if (!PyObject_CallOneArg(route_warn, message))
        {
            Py_DECREF(message);
            return -2;
        }
        #endif

        return 0;
    }

    ViewApp *self;
    route *r;
    PyObject *scope;
    PyObject *send;
    bool handler_was_called;

    puts("2");
    if (
        PyAwaitable_UnpackValues(
            awaitable,
            &self,
            NULL,
            NULL,
            &send,
            NULL
        ) < 0
    )
        return -1;

    const char *method_str;

    if (
        PyAwaitable_UnpackArbValues(
            awaitable,
            &r,
            NULL,
            NULL,
            &method_str
        ) < 0
    )
        return -1;

    int is_http;

    if (PyAwaitable_UnpackIntValues(awaitable, &is_http) < 0)
        return -1;

<<<<<<< HEAD
    if (PyErr_GivenExceptionMatches(err, self->error_type))
=======
    puts("3");
    if (((PyObject *) Py_TYPE(err)) == self->error_type)
>>>>>>> b9b43de5bfda018d39bedd5d278e1e1db3c8bf58
    {
        puts("4");
        PyObject *status_obj = PyObject_GetAttrString(
            err,
            "status"
        );
        if (!status_obj)
            return -2;

        PyObject *msg_obj = PyObject_GetAttrString(
            err,
            "message"
        );

        if (!msg_obj)
        {
            Py_DECREF(status_obj);
            return -2;
        }

        int status = PyLong_AsLong(status_obj);
        if ((status == -1) && PyErr_Occurred())
        {
            Py_DECREF(status_obj);
            Py_DECREF(msg_obj);
            return -2;
        }

        puts("5");
        const char *message = NULL;

        if (msg_obj != Py_None)
        {
            message = PyUnicode_AsUTF8(msg_obj);
            if (!message)
            {
                Py_DECREF(status_obj);
                Py_DECREF(msg_obj);
                return -2;
            }
        }

        if (
            fire_error(
                self,
                awaitable,
                status,
                r,
                NULL,
                message,
                method_str,
                is_http
            ) < 0
        )
        {
            Py_DECREF(status_obj);
            Py_DECREF(msg_obj);
            return -2;
        }

        Py_DECREF(status_obj);
        Py_DECREF(msg_obj);
        puts("6");
        return 0;
    }

    if (!is_http)
    {
        // send a websocket error code
        PyObject *send_dict;
        if (self->dev)
        {
            PyObject *str = PyObject_Str(err);
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
        } else
            send_dict = Py_BuildValue(
                "{s:s,s:i}",
                "type",
                "websocket.close",
                "code",
                1006
            );

        if (!send_dict)
            return -1;

        PyObject *coro = PyObject_Vectorcall(
            send,
            (PyObject *[]){send_dict},
            1,
            NULL
        );
        Py_DECREF(send_dict);

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

        PyErr_SetRaisedException(err);
        PyErr_Print();

        return 0;
    }

    puts("7");
    if (
        server_err_exc(
            self,
            awaitable,
            500,
            r,
            &handler_was_called,
            err,
            method_str
        ) < 0
    )
    {
        return -1;
    }

    puts("8");
    if (!handler_was_called)
    {
        // err is a borrowed reference, and PyErr_SetRaisedException steals it!
        PyErr_SetRaisedException(Py_NewRef(err));
        PyErr_Print();
    }

    puts("9");
    return 0;
}

int
load_errors(route *r, PyObject *dict)
{
    PyObject *iter = PyObject_GetIter(dict);
    PyObject *key;
    PyObject *value;

    while ((key = PyIter_Next(iter)))
    {
        value = PyDict_GetItem(
            dict,
            key
        );
        if (!value)
        {
            Py_DECREF(iter);
            return -1;
        }

        int status_code = PyLong_AsLong(key);
        if (status_code == -1)
        {
            Py_DECREF(iter);
            return -1;
        }

        if (status_code < 400 || status_code > 511)
        {
            PyErr_Format(
                PyExc_ValueError,
                "%d is not a valid status code",
                status_code
            );
            Py_DECREF(iter);
            return -1;
        }

        if (status_code >= 500)
        {
            r->server_errors[status_code - 500] = Py_NewRef(value);
        } else
        {
            uint16_t index = hash_client_error(status_code);
            if (index == 600)
            {
                PyErr_Format(
                    invalid_status_error,
                    "%d is not a valid status code",
                    status_code
                );
                return -1;
            }
            r->client_errors[index] = Py_NewRef(value);
        }
    }

    Py_DECREF(iter);

    if (PyErr_Occurred())
        return -1;
    return 0;
}
