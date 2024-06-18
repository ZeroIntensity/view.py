#ifndef VIEW_INPUTS_H
#define VIEW_INPUTS_H

#include <Python.h> // PyObject, Py_ssize_t

#include <view/typecodes.h> // type_info

typedef struct _app_parsers {
    PyObject* query;
    PyObject* json;
} app_parsers;

int body_inc_buf(PyObject* awaitable, PyObject* result);

PyObject* query_parser(
    app_parsers* parsers,
    const char* data
);

typedef struct _route_input {
    int route_data; // If this is above 0, assume all other items are undefined.
    type_info** types;
    Py_ssize_t types_size;
    PyObject* df;
    PyObject** validators;
    Py_ssize_t validators_size;
    char* name;
    bool is_body;
} route_input;

PyObject* build_data_input(
    int num,
    PyObject* app,
    PyObject* scope,
    PyObject* receive,
    PyObject* send
);

typedef struct _ViewApp ViewApp; // Including "app.h" is a circular dependency

PyObject** generate_params(
    ViewApp* app,
    app_parsers* parsers,
    const char* data,
    PyObject* query,
    route_input** inputs,
    Py_ssize_t inputs_size,
    PyObject* scope,
    PyObject* receive,
    PyObject* send
);

#endif
