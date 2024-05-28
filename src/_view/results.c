#include <Python.h>

#include <view/backport.h>
#include <view/results.h>
#include <view/view.h> // route_log


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
        &PyBytes_Type
               )) {
        const char* tmp = PyBytes_AsString(target);
        if (!tmp) return -1;
        *res_str = strdup(tmp);
    } else if (Py_IS_TYPE(
        target,
        &PyDict_Type
               )) {
        PyObject* item;
        PyObject* v;
        Py_ssize_t pos = 0;

        while (PyDict_Next(
            target,
            &pos,
            &item,
            &v
               )) {
            const char* v_str = PyUnicode_AsUTF8(v);
            if (!v_str) {
                return -1;
            }

            PyObject* item_bytes = PyUnicode_EncodeLocale(
                item,
                "strict"
            );

            if (!item_bytes) {
                return -1;
            }

            PyObject* header_list = PyTuple_New(2);

            if (!header_list) {
                Py_DECREF(item_bytes);
                return -1;
            }

            if (PyTuple_SetItem(
                header_list,
                0,
                item_bytes
                ) < 0) {
                Py_DECREF(header_list);
                Py_DECREF(item_bytes);
                return -1;
            };

            Py_DECREF(item_bytes);

            PyObject* v_bytes = PyBytes_FromString(v_str);

            if (!v_bytes) {
                Py_DECREF(header_list);
                return -1;
            }

            if (PyTuple_SetItem(
                header_list,
                1,
                v_bytes
                ) < 0) {
                Py_DECREF(header_list);
                return -1;
            };

            Py_DECREF(v_bytes);

            if (PyList_Append(
                headers,
                header_list
                ) < 0) {
                Py_DECREF(header_list);
                return -1;
            }
            Py_DECREF(header_list);
        }

        if (PyErr_Occurred()) return -1;
    } else if (Py_IS_TYPE(
        target,
        &PyLong_Type
               )) {
        *status = (int) PyLong_AsLong(target);
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

static int handle_result_impl(
    PyObject* raw_result,
    char** res_target,
    int* status_target,
    PyObject** headers_target
) {
    char* res_str = NULL;
    int status = 200;
    PyObject* headers = PyList_New(0);
    PyObject* result;

    PyObject* view_result = PyObject_GetAttrString(
        raw_result,
        "__view_result__"
    );
    PyErr_Clear();

    if (view_result) {
        result = PyObject_CallNoArgs(view_result);
        if (!result)
            return -1;
    } else result = raw_result;

    if (PyUnicode_CheckExact(
        result
        )) {
        const char* tmp = PyUnicode_AsUTF8(result);
        if (!tmp) return -1;
        res_str = strdup(tmp);
    } else if (PyBytes_CheckExact(result)) {
        const char* tmp = PyBytes_AsString(result);
        if (!tmp) return -1;
        res_str = strdup(tmp);
    } else if (PyTuple_CheckExact(
        result
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

            if (third && find_result_for(
                third,
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

    *res_target = res_str;
    *status_target = status;
    *headers_target = headers;
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
