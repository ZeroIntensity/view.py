#ifndef VIEW_HANDLING_H
#define VIEW_HANDLING_H

#include <Python.h>
#include <stdbool.h> // bool
#include <view/route.h> // route

int handle_route_callback(
    PyObject* awaitable,
    PyObject* result
);
int handle_route(PyObject* awaitable, char* query);
int handle_route_impl(
    PyObject* awaitable,
    char* body,
    char* query
);
int handle_route_query(PyObject* awaitable, char* query);
void route_free(route* r);
int send_raw_text(
    PyObject* awaitable,
    PyObject* send,
    int status,
    const char* res_str,
    PyObject* headers,     /* may be NULL */
    bool is_http
);
int handle_route_websocket(PyObject* awaitable, PyObject* result);

#endif
