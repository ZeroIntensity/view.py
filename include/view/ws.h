#ifndef VIEW_WS_H
#define VIEW_WS_H

#include <Python.h>
#include <view/backport.h>

extern PyTypeObject WebSocketType;
PyObject* ws_from_data(PyObject* scope, PyObject* send, PyObject* receive);
int handle_route_websocket(PyObject* awaitable, PyObject* result);

#endif
