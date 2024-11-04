#ifndef VIEW_RESULTS_H
#define VIEW_RESULTS_H

#include <Python.h> // PyObject

int handle_result(
    PyObject *raw_result,
    char **res_target,
    int *status_target,
    PyObject **headers_target,
    PyObject *raw_path,
    const char *method
);
char * pymem_strdup(const char *c, Py_ssize_t size);
PyObject * build_default_headers();

#endif
