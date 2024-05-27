#include <Python.h>

#include <view/app.h>
#include <view/awaitable.h>
#include <view/backport.h>
#include <view/errors.h> // route_error
#include <view/inputs.h> // route_input
#include <view/parsers.h>
#include <view/routing.h> // route, handle_route_impl

typedef struct _app_parsers app_parsers;
typedef PyObject** (* parserfunc)(app_parsers*, const char*, PyObject*,
                                  route_input**, Py_ssize_t);


int body_inc_buf(PyObject* awaitable, PyObject* result) {
    PyObject* body = PyDict_GetItemString(
        result,
        "body"
    );

    if (!body) {
        return PyErr_BadASGI();
    }

    PyObject* more_body = PyDict_GetItemString(
        result,
        "more_body"
    );
    if (!more_body) {
        Py_DECREF(body);
        return PyErr_BadASGI();
    }

    char* buf_inc;
    Py_ssize_t buf_inc_size;

    if (PyBytes_AsStringAndSize(
        body,
        &buf_inc,
        &buf_inc_size
        ) < 0) {
        Py_DECREF(body);
        Py_DECREF(more_body);
        return -1;
    }

    char* buf;
    Py_ssize_t* size;
    char* query;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &buf,
        &size,
        &query
        ) < 0) {
        Py_DECREF(body);
        Py_DECREF(more_body);
        return -1;
    }

    char* nbuf = realloc(
        buf,
        (*size) + buf_inc_size
    );

    if (!nbuf) {
        Py_DECREF(body);
        Py_DECREF(more_body);
        return -1;
    }

    strcat(
        nbuf,
        buf_inc
    );
    PyAwaitable_SetArbValue(
        awaitable,
        0,
        nbuf
    );
    *size = (*size) + buf_inc_size;

    PyObject* aw;
    PyObject* receive;

    if (PyAwaitable_UnpackValues(
        awaitable,
        &aw,
        &receive
        ) < 0) {
        Py_DECREF(more_body);
        Py_DECREF(body);
        return -1;
    }

    if (PyObject_IsTrue(more_body)) {
        PyObject* receive_coro = PyObject_CallNoArgs(receive);

        if (PyAwaitable_AddAwait(
            awaitable,
            receive_coro,
            body_inc_buf,
            NULL
            ) < 0) {
            Py_DECREF(more_body);
            Py_DECREF(body);
            Py_DECREF(receive_coro);
            free(query);
            free(nbuf);
            return -1;
        }

        Py_DECREF(receive_coro);
    } else {
        if (handle_route_impl(
            aw,
            nbuf,
            query
            ) < 0) {
            Py_DECREF(more_body);
            Py_DECREF(body);
            free(nbuf);
            return -1;
        };
    }

    Py_DECREF(more_body);
    Py_DECREF(body);

    return 0;
}

int handle_route_query(PyObject* awaitable, char* query) {
    ViewApp* self;
    route* r;
    PyObject** path_params;
    Py_ssize_t* size;
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
        ) < 0)
        return -1;

    const char* method_str;

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        NULL,
        NULL,
        NULL,
        &method_str
        ) <
        0)
        return -1;

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

    if (PyAwaitable_UnpackArbValues(
        awaitable,
        &r,
        &path_params,
        &size,
        NULL
        ) < 0) {
        Py_DECREF(query_obj);
        return -1;
    }

    Py_ssize_t fake_size = 0;

    if (size == NULL)
        size = &fake_size;
    PyObject** params = calloc(
        r->inputs_size,
        sizeof(PyObject*)
    );
    if (!params) {
        Py_DECREF(query_obj);
        return -1;
    }
    Py_ssize_t final_size = 0;

    for (int i = 0; i < r->inputs_size; i++) {
        if (r->inputs[i]->route_data) {
            PyObject* data = build_data_input(
                r->inputs[i]->route_data,
                scope,
                receive,
                send
            );
            if (!data) {
                for (int i = 0; i < r->inputs_size; i++)
                    Py_XDECREF(params[i]);

                free(params);
                Py_DECREF(query_obj);
                return -1;
            }

            params[i] = data;
            ++final_size;
            continue;
        }

        PyObject* item = PyDict_GetItemString(
            query_obj,
            r->inputs[i]->name
        );

        if (!item) {
            if (r->inputs[i]->df) {
                params[i] = r->inputs[i]->df;
                ++final_size;
                continue;
            }

            for (int i = 0; i < r->inputs_size; i++)
                Py_XDECREF(params[i]);

            free(params);
            Py_DECREF(query_obj);
            return fire_error(
                self,
                awaitable,
                400,
                r,
                NULL,
                NULL,
                method_str
            );
        } else ++final_size;

        if (item) {
            PyObject* parsed_item = cast_from_typecodes(
                r->inputs[i]->types,
                r->inputs[i]->types_size,
                item,
                self->parsers.json,
                true
            );
            if (!parsed_item) {
                PyErr_Clear();
                for (int i = 0; i < r->inputs_size; i++)
                    Py_XDECREF(params[i]);

                free(params);
                Py_DECREF(query_obj);
                return fire_error(
                    self,
                    awaitable,
                    400,
                    r,
                    NULL,
                    NULL,
                    method_str
                );
            }
            params[i] = parsed_item;
        }
    }

    PyObject** merged = PyMem_Calloc(
        final_size + (*size),
        sizeof(PyObject*)
    );

    if (!merged) {
        PyErr_NoMemory();
        return -1;
    }

    for (int i = 0; i < (*size); i++)
        merged[i] = path_params[i];

    for (int i = 0; i < final_size; i++)
        merged[*size + i] = params[i];

    PyObject* coro = PyObject_VectorcallDict(
        r->callable,
        merged,
        *size + final_size,
        NULL
    );

    for (int i = 0; i < final_size + *size; i++)
        Py_XDECREF(merged[i]);

    PyMem_Free(merged);
    free(params);
    Py_DECREF(query_obj);

    if (!coro)
        return -1;

    if (PyAwaitable_AddAwait(
        awaitable,
        coro,
        handle_route_callback,
        route_error
        ) < 0) {
        Py_DECREF(coro);
        return -1;
    }

    Py_DECREF(coro);
    return 0;
}

PyObject* query_parser(
    app_parsers* parsers,
    const char* data
) {
    PyObject* py_str = PyUnicode_FromString(data);

    if (!py_str)
        return NULL;

    PyObject* obj = PyObject_Vectorcall(
        parsers->query,
        (PyObject*[]) { py_str },
        1,
        NULL
    );

    Py_DECREF(py_str);
    return obj; // no need for null check
}
