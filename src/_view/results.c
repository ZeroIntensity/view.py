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

#include <view/util.h> // View_Strdup
#include <view/response.h>

/*
 * Generate the "default response headers" (i.e. headers that
 * are sent when no headers are explicitly set by the user.)
 *
 * This returns a new strong reference. However, this should
 * only be called once per program, by the module initialization
 * function. The result is stored globally as `default_headers`.
 */
PyObject *
View_BuildDefaultHeaders()
{
    // [("content-type", "text/plain")]
    return Py_BuildValue("[(y, y)]", "content-type", "text/plain");
}

/*
 * Convert a dictionary of {key: value} pairs to a list of [(key, value)] pairs.
 */
static int
flatten_dict(PyObject *dict, PyObject *tuple)
{
    PyObject *key;
    PyObject *value;
    Py_ssize_t pos = 0;

    while (PyDict_Next(dict, &pos, &key, &value))
    {
        PyObject *key_bytes = PyUnicode_AsEncodedString(
            key,
            "utf-8",
            "strict"
        );

        if (!key_bytes)
        {
            return -1;
        }

        PyObject *value_bytes = PyUnicode_AsEncodedString(
            value,
            "utf-8",
            "strict"
        );
        if (!value_bytes)
        {
            Py_DECREF(key_bytes);
            return -1;
        }

        PyObject *header = PyTuple_New(2);
        if (!header)
        {
            Py_DECREF(key_bytes);
            Py_DECREF(value_bytes);
            return -1;
        }
        // PyTuple_SET_ITEM steals the reference, no need to Py_DECREF
        PyTuple_SET_ITEM(header, 0, key_bytes);
        PyTuple_SET_ITEM(header, 1, value_bytes);

        // pos does not start at 0, it starts at 1
        PyTuple_SET_ITEM(tuple, pos - 1, header);
    }

    return 0;
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
    ViewResponse *response
)
{
    assert(!PyErr_Occurred());
    if (PyUnicode_CheckExact(result))
    {
        // TODO: Cache this
        response->headers_list = View_BuildDefaultHeaders();
        if (response->headers_list == NULL)
        {
            return -1;
        }
        response->body = Py_NewRef(result);
        response->status_code = PyLong_FromLong(200);
        return 0;
    }

    if (!PyTuple_CheckExact(result))
    {
        // TODO: Debugging
        PyErr_Format(
            PyExc_TypeError,
            "expected a route to return a string or tuple, got %R",
            result
        );
        return -1;
    }

    assert(PyTuple_CheckExact(result));
    if (PyTuple_GET_SIZE(result) > 3 || PyTuple_GET_SIZE(result) < 2)
    {
        // TODO: Display tuple
        PyErr_SetString(
            PyExc_TypeError,
            "returned tuple should be between 2 and 3 elements"
        );
        return -1;
    }

    PyObject *body = PyTuple_GET_ITEM(
        result,
        0
    );
    PyObject *status = PyTuple_GET_ITEM(
        result,
        1
    );
    response->body = Py_NewRef(body);
    response->status_code = Py_NewRef(status);

    assert(!PyErr_Occurred());
    if (!PyLong_CheckExact(status))
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected second value of response to be an int, got %R",
            status
        );
        return -1;
    }

    if (PyTuple_GET_SIZE(result) == 2)
    {
        response->headers_list = View_BuildDefaultHeaders();
        if (response->headers_list == NULL)
        {
            return -1;
        }
        return 0;
    }

    assert(PyTuple_GET_SIZE(result) == 3);
    PyObject *headers = PyTuple_GET_ITEM(result, 3);

    if (PyList_CheckExact(headers) || PyTuple_CheckExact(headers))
    {
        /*
         * Undocumented because I don't want the user to touch it!
         * This is a way for a route to return a raw ASGI header list, which allows
         * for faster and multi-headers.
         */
        response->headers_list = Py_NewRef(headers);
        return 0;
    }

    if (!PyDict_CheckExact(headers))
    {
        PyErr_Format(
            PyExc_TypeError,
            "expected third value of response to be a dict, got %R",
            headers
        );
        return -1;
    }

    PyObject *header_tup = PyTuple_New(PyDict_GET_SIZE(headers));
    if (!header_tup)
    {
        return -1;
    }

    if (flatten_dict(headers, header_tup) < 0)
    {
        Py_DECREF(header_tup);
        return -1;
    }

    return 0;
}

/*
 * Generate HTTP response components (i.e. the body, status, and headers) from
 * a route return value.
 */
int
ViewResult_ToResponse(
    PyObject *raw_result,
    ViewResponse *response
)
{
    assert(raw_result != NULL);
    assert(response != NULL);
    assert(response->request != NULL);
    Py_INCREF(raw_result);
    int res = handle_result_impl(raw_result, response);
    Py_DECREF(raw_result);

    // TODO: Implement route logging here.
    return res;
}
