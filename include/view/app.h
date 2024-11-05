#ifndef VIEW_APP_H
#define VIEW_APP_H

#include <Python.h> // PyObject, PyTypeObject
#include <stdbool.h> // bool

#include <view/map.h>

typedef struct _route ViewRoute;

typedef enum _request_type
{
    HTTP = 1 << 0,
    WEBSOCKET = 1 << 1
} ViewRequest_Type;

typedef struct _app_state
{
    bool dev;
} ViewApp_State;

typedef struct _error_state
{
    PyObject *client_errors[28];
    PyObject *server_errors[11];
    PyObject *exceptions_dict;
} ViewApp_ErrorState;

typedef struct _route_state
{
    ViewMap *get;
    ViewMap *post;
    ViewMap *put;
    ViewMap *patch;
    ViewMap *delete;
    ViewMap *options;
    ViewMap *websocket;
    ViewMap *all_routes;
} ViewApp_RouteState;

typedef struct _lifecycle_state
{
    PyObject *startup;
    PyObject *cleanup;
} ViewApp_LifecycleState;

typedef struct _app
{
    PyObject_HEAD
    ViewApp_State state;
    ViewApp_LifecycleState lifecycle;
    ViewApp_RouteState routes;
    ViewApp_ErrorState errors;
} ViewApp;

#endif
