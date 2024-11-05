#ifndef VIEW_INPUTS_H
#define VIEW_INPUTS_H

#include <Python.h> // PyObject, Py_ssize_t

#include <view/array.h>
#include <view/typecodes.h>
#include <view/request.h>

int _ViewParse_IncrementBuf(PyObject *awaitable, PyObject *result);
PyObject * ViewParse_Query(const char *data);

typedef uint16_t ViewRouteInput_DataID;

typedef struct _external_input
{
    char *name;
    bool is_body;
    ViewArray typecodes;
    ViewArray validators;
    PyObject *default_object;
} ViewRouteInput_External;

typedef union _route_input
{
    ViewRouteInput_DataID data;
    ViewRouteInput_External external;
} ViewRouteInput;

PyObject * ViewRouteInput_BuildData(
    int id,
    ViewRequest *request
);

PyObject ** ViewParse_GenerateRouteArgs(ViewRequest *request);

#endif
