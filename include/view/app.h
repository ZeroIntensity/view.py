#ifndef VIEW_APP_H
#define VIEW_APP_H

#include <Python.h>
#include <stdbool.h> // bool

#include <view/parsers.h> // app_parsers
#include <view/map.h> // map

extern PyTypeObject ViewAppType;
int PyErr_BadASGI(void);

typedef struct _ViewApp {
    PyObject_HEAD
    PyObject* startup;
    PyObject* cleanup;
    map* get;
    map* post;
    map* put;
    map* patch;
    map* delete;
    map* options;
    map* websocket;
    map* all_routes;
    PyObject* client_errors[28];
    PyObject* server_errors[11];
    bool dev;
    PyObject* exceptions;
    app_parsers parsers;
    bool has_path_params;
    PyObject* error_type;
} ViewApp;

int PyErr_BadASGI(void);

#endif
