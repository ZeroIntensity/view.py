#ifndef VIEW_TYPECODES_H
#define VIEW_TYPECODES_H

#include <Python.h> // PyObject, PyTypeObject
#include <stdbool.h> // bool

typedef struct _route ViewRoute;

extern PyTypeObject TCPublicType;

typedef enum
{
    STRING_ALLOWED = 1 << 0,
    NULL_ALLOWED = 2 << 0
} ViewTypeCode_Flag;

typedef struct _typecode ViewTypeCode;

struct _typecode
{
    uint8_t typecode;
    PyObject *ob;
    ViewTypeCode **children;
    Py_ssize_t children_size;
    PyObject *df;
};

bool ViewRouteInput_HasBodyParameter(PyObject *inputs);

int ViewTypeCode_LoadIntoRoute(
    ViewRoute *r,
    PyObject *target
);

PyObject *
ViewTypeCode_CastObject(
    ViewTypeCode **codes,
    Py_ssize_t len,
    PyObject *item,
    PyObject *json_parser,
    bool allow_casting
);
ViewTypeCode ** ViewTypeCode_FromList(PyObject *type_codes, Py_ssize_t len);
void ViewTypeCode_Free(ViewTypeCode **codes, Py_ssize_t len);

#endif
