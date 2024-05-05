#ifndef VIEW_RESULTS_H
#define VIEW_RESULTS_H

#include <Python.h> // PyObject

int handle_result(
    PyObject* raw_result,
    char** res_target,
    int* status_target,
    PyObject** headers_target,
    PyObject* raw_path,
    const char* method
);

#endif