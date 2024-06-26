/*
 * view.py route results implementation
 *
 * This file is responsible for parsing route responses.
 *
 * Note that this implementation does not actually send
 * ASGI responses. Instead, it generates the necessary
 * components to send a response (which is done by the handler).
 *
 * This is also not responsible for calling __view_result__(), since
 * that would require generating a Context()
 *
 * All this does, is given a flattened result (i.e. __view_result__() was already called), extract
 * the three needed components for an ASGI response. If some components are missing, then default
 * ones are used.
 *
 * For example, given b"hello world" as result, this would be in charge of turning that
 * into a "hello world" C string on the heap, as well as setting the status code to 200 and
 * using the default headers.
 *
 * If it was given a tuple, such as (b"hello world", 201), then it would once again get the
 * C string, then set the status to 201, and then use the default headers.
 *
 * Historically, view.py used to support doing this in any order (e.g. returning the
 * tuple `(b"hello world", 201)` would be equivalent to `(201, b"hello world")`)
 *
 * For performance and versatility reasons, this was removed.
 */
#include <Python.h>

#include <view/backport.h>
#include <view/results.h>
#include <view/view.h> // route_log

/*
 * Implementation of strdup() using PyMem_Malloc()
 *
 * Unlike strdup(), this takes a size parameter. Try
 * to avoid using strlen(), and use a function that includes
 * the string size, such as PyUnicode_AsUTF8AndSize()
 *
 * Strings that are returned by this function should
 * be freed using PyMem_Free(), not free()
 *
 * Technically speaking, this is more or less a copy
 * of CPython's private _PyMem_Strdup function.
 */
char *
pymem_strdup(const char *c, Py_ssize_t size)
{
    char *buf = PyMem_Malloc(size + 1); // Length with null terminator
    if (!buf)
        return (char *) PyErr_NoMemory();
    memcpy(buf, c, size + 1);
    return buf;
}

/*
 * Get a duplicated string of a Python string or bytes object.
 *
 * If the object is not a string or bytes, this throws a TypeError
 * and returns NULL.
 *
 * This uses pymem_strdup(), so strings returned by this function
 * should be deallocated via PyMem_Free()
 */
static char *
handle_response_body(PyObject *target)
{
    if (PyUnicode_CheckExact(target))
    {
        Py_ssize_t size;
        const char *tmp = PyUnicode_AsUTF8AndSize(target, &size);
        if (!tmp) return NULL;
        return pymem_strdup(tmp, size);
    } else if (PyBytes_CheckExact(target))
    {
        Py_ssize_t size;
        char *tmp;
        if (PyBytes_AsStringAndSize(target, &tmp, &size) < 0)
            return NULL;
        return pymem_strdup(tmp, size);
    } else
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected a str or bytes response body, got %R",
            target
        );
        return NULL;
    }
}

/*
 * Generate the "default response headers" (i.e. headers that
 * are sent when no headers are explicitly set by the user.)
 *
 * This returns a new strong reference. However, this should
 * only be called once per program, by the module initialization
 * function. The result is stored globally as `default_headers`.
 */
PyObject *
build_default_headers()
{
    PyObject *tup = PyTuple_New(1);
    if (!tup)
        return NULL;

    PyObject *content_type = PyTuple_New(2);
    if (!content_type)
    {
        Py_DECREF(tup);
        return NULL;
    }

    PyObject *key = PyBytes_FromString("content-type");
    if (!key)
    {
        Py_DECREF(tup);
        Py_DECREF(content_type);
        return NULL;
    }

    PyObject *val = PyBytes_FromString("text/plain");
    if (!val)
    {
        Py_DECREF(key);
        Py_DECREF(tup);
        Py_DECREF(content_type);
        return NULL;
    }

    PyTuple_SET_ITEM(content_type, 0, key);
    PyTuple_SET_ITEM(content_type, 1, val);
    PyTuple_SET_ITEM(tup, 0, content_type);
    return tup;
}

/*
 * The raw implementation of handling results.
 *
 * Unlike the exported handle_result(), this does not write to
 * the route log.
 */
static int
handle_result_impl(
    PyObject *result,
    char **res_target,
    int *status_target,
    PyObject **headers_target
)
{
    char *res_str = NULL;
    int status = 200;
    PyErr_Clear();

    res_str = handle_response_body(result);
    if (!res_str)
    {
        if (!PyTuple_CheckExact(result))
            return -1;

        PyErr_Clear();
        if (PySequence_Size(result) > 3)
        {
            PyErr_SetString(
                PyExc_TypeError,
                "returned tuple should not exceed 3 elements"
            );
            return -1;
        }

        PyObject *first = PyTuple_GetItem(
            result,
            0
        );
        PyObject *second = PyTuple_GetItem(
            result,
            1
        );
        PyObject *third = PyTuple_GetItem(
            result,
            2
        );

        PyErr_Clear();
        res_str = handle_response_body(first);
        if (!res_str)
            return -1;

        if (!second)
        {
            // exit early
            *res_target = res_str;
            *status_target = 200;
            *headers_target = Py_NewRef(default_headers);
            return 0;
        }

        if (!PyLong_CheckExact(second))
        {
            PyErr_Format(
                PyExc_TypeError,
                "expected second value of response to be an int, got %R",
                second
            );
            return -1;
        }

        status = PyLong_AsLong(second);
        if (status == -1)
        {
            PyMem_Free(res_str);
            return -1;
        }

        if (!third)
        {
            // exit early
            *res_target = res_str;
            *status_target = status;
            *headers_target = Py_NewRef(default_headers);
            return 0;
        }

        if (PyList_CheckExact(third) || PyTuple_CheckExact(third))
        {
            /*
             * Undocumented because I don't want the user to touch it!
             * This is a way for a route to return a raw ASGI header list, which allows
             * for faster and multi-headers.
             */
            *res_target = res_str;
            *status_target = status;
            *headers_target = Py_NewRef(third);
            return 0;
        }

        if (!PyDict_CheckExact(third))
        {
            PyErr_Format(
                PyExc_TypeError,
                "expected third value of response to be a dict, got %R",
                third
            );
            return -1;
        }

        PyObject *header_tup = PyTuple_New(PyDict_GET_SIZE(third));
        if (!header_tup)
        {
            PyMem_Free(res_str);
            return -1;
        }

        PyObject *key;
        PyObject *value;
        Py_ssize_t pos = 0;

        while (PyDict_Next(third, &pos, &key, &value))
        {
            PyObject *header = PyTuple_New(2);
            if (!header)
            {
                PyMem_Free(res_str);
                Py_DECREF(header_tup);
                return -1;
            }
            PyTuple_SET_ITEM(header, 0, Py_NewRef(key));
            PyTuple_SET_ITEM(header, 1, Py_NewRef(value));

            // this steals the reference, no need to decref
            PyTuple_SET_ITEM(header_tup, pos - 1, header);
        }


        *res_target = res_str;
        *status_target = status;
        *headers_target = header_tup;
        return 0;
    }

    *res_target = res_str;
    *status_target = status;
    *headers_target = Py_NewRef(default_headers);
    return 0;
}

/*
 * Generate HTTP response components (i.e. the body, status, and headers) from
 * a route return value.
 *
 * The result passed should be a tuple, or body string. This function
 * does not call __view_result__(), as that is up to the caller.
 *
 * The body output parameter will be a string on the heap,
 * and is responsible for deallocating it with PyMem_Free()
 *
 * The status output parameter can be *any* integer (including non-HTTP
 * status codes). Validation is up to the caller.
 *
 * The headers will always be an ASGI headers iterable [(bytes_key, bytes_value), ...]
 *
 * If this function fails, the caller is not responsible for
 * deallocating or managing references of any of the parameters.
 */
int
handle_result(
    PyObject *raw_result,
    char **res_target,
    int *status_target,
    PyObject **headers_target,
    PyObject *raw_path,
    const char *method
)
{
    /*
     * This calls handle_result_impl() internally, but
     * this function is the actual interface for handling a return value.
     *
     * The only extra thing that this does is write to the route log.
     */
    int res = handle_result_impl(
        raw_result,
        res_target,
        status_target,
        headers_target
    );

    return res;
    if (res < 0)
        return -1;

    if (!route_log) return res;

    PyObject *args = Py_BuildValue(
        "(iOs)",
        *status_target,
        raw_path,
        method
    );

    if (!args)
        return -1;

    /*
     * A lot of errors related to memory corruption are traced
     * to here by debuggers.
     *
     * This is, more or less, a false positive! It's quite
     * unlikely that the actual cause of the issue is here.
     */
    PyObject *result = PyObject_Call(
        route_log,
        args,
        NULL
    );

    if (!result)
    {
        Py_DECREF(args);
        return -1;
    }

    Py_DECREF(result);
    Py_DECREF(args);

    return res;
}
