#ifndef VIEW_WS_H
#define VIEW_WS_H

#include <Python.h>
#include <view/backport.h>

extern PyTypeObject WebSocketType;
PyObject* ws_from_data(PyObject* send, PyObject* receive);

#endif
