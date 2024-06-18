#ifndef VIEW_TYPECODES_H
#define VIEW_TYPECODES_H

#include <Python.h> // PyObject, PyTypeObject
#include <stdbool.h> // bool

typedef struct Route route; // route.h depends on this file
extern PyTypeObject TCPublicType;

typedef enum {
    STRING_ALLOWED = 1 << 0,
    NULL_ALLOWED = 2 << 0
} typecode_flag;

typedef struct _type_info type_info;

struct _type_info {
    uint8_t typecode;
    PyObject* ob;
    type_info** children;
    Py_ssize_t children_size;
    PyObject* df;
};

bool figure_has_body(PyObject* inputs);

int load_typecodes(
    route* r,
    PyObject* target
);

PyObject* cast_from_typecodes(
    type_info** codes,
    Py_ssize_t len,
    PyObject* item,
    PyObject* json_parser,
    bool allow_casting
);
type_info** build_type_codes(PyObject* type_codes, Py_ssize_t len);
void free_type_codes(type_info** codes, Py_ssize_t len);

#endif
