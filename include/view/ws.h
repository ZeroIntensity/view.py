#ifndef VIEW_WS_H
#define VIEW_WS_H

#include <Python.h>

#include <view/results.h>

extern PyTypeObject ViewWebSocket_Type;
PyObject * ViewWebSocket_FromData(ViewRequest *request);

#endif
