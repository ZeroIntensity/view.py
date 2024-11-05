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
    uint16_t status_code;
    const char *response_text;
    PyObject *headers_list;
} ViewResponse;

int ViewResponse_Send(ViewResponse *response);

#endif
