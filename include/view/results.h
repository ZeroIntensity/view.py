#ifndef VIEW_RESULTS_H
#define VIEW_RESULTS_H

#include <Python.h> // PyObject

int ViewResult_Handle(
    PyObject *raw_result,
    char **res_target,
    int *status_target,
    PyObject **headers_target,
    PyObject *raw_path,
    const char *method
);
char * ViewUtil_Strdup(const char *c, Py_ssize_t size);
PyObject * ViewUtil_BuildDefaultHeaders();

#endif
