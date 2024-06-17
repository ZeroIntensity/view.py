#include <Python.h>

#include <view/backport.h>
#include <view/results.h>
#include <view/view.h> // route_log

char* pymem_strdup(const char* c, Py_ssize_t size) {
    char* buf = PyMem_Malloc(size + 1); // length with null terminator
    if (!buf)
        return (char*) PyErr_NoMemory();
    memcpy(buf, c, size + 1);
    return buf;
}

static char* handle_response_body(PyObject* target) {
    if (PyUnicode_CheckExact(target)) {
        Py_ssize_t size;
        const char* tmp = PyUnicode_AsUTF8AndSize(target, &size);
        if (!tmp) return NULL;
        return pymem_strdup(tmp, size);
    } else if (PyBytes_CheckExact(target)) {
        Py_ssize_t size;
        char* tmp;
        if (PyBytes_AsStringAndSize(target, &tmp, &size) < 0)
            return NULL;
        return pymem_strdup(tmp, size);
    } else {
        PyErr_Format(PyExc_TypeError,
            "expected a str or bytes response body, got %R", target);
        return NULL;
    }
}

/*
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
        Py_ssize_t size;
        const char* tmp = PyUnicode_AsUTF8AndSize(target, &size);
        if (!tmp) return -1;
 * res_str = pymem_strdup(tmp, size);
    } else if (Py_IS_TYPE(
        target,
        &PyBytes_Type
               )) {
        Py_ssize_t size;
        char* tmp;
        if (PyBytes_AsStringAndSize(target, &tmp, &size) < 0)
            return -1;
 * res_str = pymem_strdup(tmp, size);
    } else if (Py_IS_TYPE(
        target,
        &PyDict_Type
               )) {
    }

    if (PyErr_Occurred()) return -1;
   }
   else if (Py_IS_TYPE(
    target,
    &PyLong_Type
         )) {
 * status = (int) PyLong_AsLong(target);
   } else if (Py_IS_TYPE(
    target,
    &PyTuple_Type
           )) {

    for (Py_ssize_t i = 0; i < PyTuple_GET_SIZE(target); i++) {
        PyObject* t_value = PyTuple_GET_ITEM(
            target,
            i
        );
        if (!PyTuple_Check(
            t_value
            )) {
            PyErr_SetString(
                PyExc_TypeError,
                "raw header tuple should contain tuples"
            );
            return -1;
        }

        PyList_Append(
            headers,
            t_value
        );
    }

    if (PyErr_Occurred()) {
        return -1;
    }
   } else {
    PyErr_SetString(
        PyExc_TypeError,
        "returned tuple should only contain a str, bytes, int, or dict"
    );
    return -1;
   }

   return 0;
   }
 */

PyObject* build_default_headers() {
    PyObject* tup = PyTuple_New(1);
    if (!tup)
        return NULL;

    PyObject* content_type = PyTuple_New(2);
    if (!content_type) {
        Py_DECREF(tup);
        return NULL;
    }

    PyObject* key = PyBytes_FromString("content-type");
    if (!key) {
        Py_DECREF(tup);
        Py_DECREF(content_type);
        return NULL;
    }

    PyObject* val = PyBytes_FromString("text/plain");
    if (!val) {
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

static int handle_result_impl(
    PyObject* result,
    char** res_target,
    int* status_target,
    PyObject** headers_target
) {
    char* res_str = NULL;
    int status = 200;
    PyErr_Clear();

    res_str = handle_response_body(result);
    if (!res_str) {
        if (!PyTuple_CheckExact(result))
            return -1;

        PyErr_Clear();
        if (PySequence_Size(result) > 3) {
            PyErr_SetString(
                PyExc_TypeError,
                "returned tuple should not exceed 3 elements"
            );
            return -1;
        }

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
        res_str = handle_response_body(first);
        if (!res_str)
            return -1;

        if (!second) {
            // exit early
            *res_target = res_str;
            *status_target = 200;
            *headers_target = Py_NewRef(default_headers);
            return 0;
        }

        if (!PyLong_CheckExact(second)) {
            PyErr_Format(PyExc_TypeError,
                "expected second value of response to be an int, got %R",
                second);
            return -1;
        }

        status = PyLong_AsLong(second);
        if (status == -1) {
            PyMem_Free(res_str);
            return -1;
        }

        if (!third) {
            // exit early
            *res_target = res_str;
            *status_target = status;
            *headers_target = Py_NewRef(default_headers);
            return 0;
        }

        if (PyList_CheckExact(third)) {
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

        if (PyDict_CheckExact(third)) {
            PyErr_Format(PyExc_TypeError,
                "expected third value of response to be a dict, got %R",
                third);
            return -1;
        }

        PyObject* header_tup = PyTuple_New(PyDict_GET_SIZE(third));
        if (!header_tup) {
            PyMem_Free(res_str);
            return -1;
        }

        PyObject* key;
        PyObject* value;
        Py_ssize_t pos = 0;

        while (PyDict_Next(third, &pos, &key, &value)) {
            PyObject* header = PyTuple_New(2);
            if (!header) {
                PyMem_Free(res_str);
                Py_DECREF(header_tup);
                return -1;
            }
            PyTuple_SET_ITEM(header, 0, Py_NewRef(key));
            PyTuple_SET_ITEM(header, 1, Py_NewRef(value));

            // this steals the reference, no need to decref
            PyTuple_SET_ITEM(header_tup, pos, header);
        }

        *headers_target = header_tup;
        *res_target = res_str;
        *status_target = status;
    }

    *res_target = res_str;
    *status_target = status;
    *headers_target = Py_NewRef(default_headers);
    return 0;
}

int handle_result(
    PyObject* raw_result,
    char** res_target,
    int* status_target,
    PyObject** headers_target,
    PyObject* raw_path,
    const char* method
) {
    int res = handle_result_impl(
        raw_result,
        res_target,
        status_target,
        headers_target
    );
    if (res < 0)
        return -1;
    if (!route_log) return res;

    PyObject* args = Py_BuildValue(
        "(iOs)",
        *status_target,
        raw_path,
        method
    );

    if (!args)
        return -1;

    if (!PyObject_Call(
        route_log,
        args,
        NULL
        )) {
        Py_DECREF(args);
        return -1;
    }
    Py_DECREF(args);

    return res;
}
