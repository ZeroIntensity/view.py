#ifndef VIEW_PARTS_H
#define VIEW_PARTS_H

#include <Python.h> // PyObject, Py_ssize_t

#include <view/app.h> // ViewApp
#include <view/map.h> // map
#include <view/route.h> // route

int extract_parts(
    ViewApp* self,
    PyObject* awaitable,
    map* target,
    char* path,
    const char* method_str,
    Py_ssize_t* size,
    route** out_r,
    PyObject*** out_params
);

int load_parts(ViewApp* app, map* routes, PyObject* parts, route* r);

#endif
