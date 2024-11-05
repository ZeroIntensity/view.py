#ifndef VIEW_HANDLING_H
#define VIEW_HANDLING_H

#include <Python.h>
#include <stdbool.h> // bool

#include <view/app.h>
#include <view/request.h>

int ViewResponse_Callback(
    PyObject *awaitable,
    PyObject *result
);

typedef struct _response
{
    ViewRequest *request;
    PyObject *status_code;
    PyObject *body;
    PyObject *headers_list;
} ViewResponse;

static inline void
ViewResponse_Clear(ViewResponse *response)
{
    assert(response != NULL);
    Py_CLEAR(response->status_code);
    Py_CLEAR(response->body);
    Py_CLEAR(response->headers_list);
    response->request = NULL;
}

int ViewResponse_Send(ViewResponse *response);

#endif
