#ifndef VIEW_REQUEST_H
#define VIEW_REQUEST_H

#include <Python.h>

#include <view/app.h>
#include <view/route.h>
#include <view/util.h> // View_AllocStructureCast

typedef enum _request_type
{
    UNSET = 1 << 0, // Default
    HTTP = 1 << 1,
    WEBSOCKET = 1 << 2
} ViewRequest_Type;

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

#define ViewRequest_New() View_AllocStructureCast(ViewRequest)

static inline void
ViewRequest_ClearASGI(ViewRequest_ASGIData *asgi)
{
    Py_CLEAR(asgi->awaitable);
    Py_CLEAR(asgi->scope);
    Py_CLEAR(asgi->receive);
    Py_CLEAR(asgi->send);
}

static inline void
ViewRequest_ClearCommon(ViewRequest_CommonData *common)
{
    Py_CLEAR(common->headers);
    Py_CLEAR(common->query);
    Py_CLEAR(common->unparsed_path);
}

static inline void
ViewRequest_Free(ViewRequest *request)
{
    ViewRequest_ClearASGI(&request->asgi);
    PyMem_Free(request);
}

#endif
