#ifndef VIEW_ERRORS_H
#define VIEW_ERRORS_H

#include <Python.h> // PyObject
#include <stdbool.h> // bool
#include <stdint.h> // uint16_t

#include <view/request.h>
#include <view/route.h>

int ViewRoute_HandleError(
    PyObject *awaitable,
    PyObject *err
);

typedef struct _error_result
{
    uint16_t status;
    bool handler_was_called;
} ViewError_Result;

int ViewError_Fire(
    ViewRequest *request,
    const char *message,
    ViewError_Result *result
);

int ViewError_SendServerSide(
    ViewRequest *request,
    ViewError_Result *result
);

int ViewError_LoadIntoRoute(ViewRoute *r, PyObject *dict);

uint16_t ViewError_GetServerIndex(int status);
uint16_t ViewError_GetClientIndex(int status);

void
ViewError_Show(ViewRequest *request);

#endif
