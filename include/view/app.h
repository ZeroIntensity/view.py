#ifndef VIEW_APP_H
#define VIEW_APP_H

#include <Python.h> // PyObject, PyTypeObject
#include <stdbool.h> // bool

#include <view/inputs.h> // app_parsers
#include <view/map.h> // map

extern PyTypeObject ViewAppType;

#if defined(__LINE__) && defined(__FILE__)
#define PyErr_BadASGI() view_PyErr_BadASGI(__FILE__, __LINE__)
#else
#define PyErr_BadASGI() view_PyErr_BadASGI("<unknown>.c", 0)
#endif

int view_PyErr_BadASGI(char *file, int lineno);

typedef struct _ViewApp
{
    PyObject_HEAD
    PyObject *startup;
    PyObject *cleanup;
    map *get;
    map *post;
    map *put;
    map *patch;
    map *delete;
    map *options;
    map *websocket;
    map *all_routes;
    PyObject *client_errors[28];
    PyObject *server_errors[11];
    bool dev;
    PyObject *exceptions;
    app_parsers parsers;
    bool has_path_params;
    PyObject *error_type;
} ViewApp;

#endif
