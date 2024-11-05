#ifndef VIEW_REQUEST_H
#define VIEW_REQUEST_H

#include <Python.h>

#include <view/app.h>
#include <view/route.h>

typedef struct _asgi_data
{
    PyObject *awaitable;
    PyObject *scope;
    PyObject *receive;
    PyObject *send;
} ViewRequest_ASGIData;

typedef struct _request_data
{
    PyObject *query;
    PyObject *headers;
    PyObject *unparsed_path;
} ViewRequest_CommonData;

typedef struct _request
{
    ViewApp *app;
    ViewRoute *route;
    ViewRequest_ASGIData asgi;
    ViewRequest_CommonData common;
    ViewRequest_Type type;
} ViewRequest;

#endif
