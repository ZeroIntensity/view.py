#ifndef VIEW_HANDLING_H
#define VIEW_HANDLING_H

#include <Python.h>
#include <stdbool.h> // bool

#include <view/app.h>
#include <view/route.h>

int ViewHandle_Callback(
    PyObject *awaitable,
    PyObject *result
);
int ViewHandle_Route(PyObject *awaitable, char *query);
int _ViewHandle_RouteImpl(
    PyObject *awaitable,
    char *body,
    char *query
);
int ViewHandle_RouteWithQuery(PyObject *awaitable, char *query);
int ViewHandle_RouteWithWebsocket(PyObject *awaitable, PyObject *result);

typedef struct
{
    ViewRequest *request;
    uint16_t status_code;
    const char *response_text;
    PyObject *headers_list;
} ViewResponse;

int ViewResponse_Send(ViewResponse *response);


#endif
