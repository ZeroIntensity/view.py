#ifndef VIEW_INPUTS_H
#define VIEW_INPUTS_H

#include <Python.h> // PyObject, Py_ssize_t

#include <view/app.h> // ViewApp
#include <view/parsers.h> // app_parsers
#include <view/typecodes.h>

typedef struct _route_input {
    int route_data; // if this is above 0, assume all other items are undefined
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
