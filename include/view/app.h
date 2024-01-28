#ifndef VIEW_APP_H
#define VIEW_APP_H

#include <Python.h>
#include <stdbool.h>
#include <view/backport.h>

extern PyTypeObject ViewAppType;
int PyErr_BadASGI(void);
typedef struct _type_info type_info;
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
