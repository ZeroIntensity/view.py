#ifndef VIEW_ROUTING_H
#define VIEW_ROUTING_H

#include <Python.h>
#include <stdbool.h> // bool
#include <stdint.h> // uint16_t

#include <view/map.h> // map
#include <view/inputs.h> // route_input

typedef struct Route route;

struct Route {
    PyObject* callable;
    char* cache;
    PyObject* cache_headers;
    uint16_t cache_status;
    Py_ssize_t cache_index;
    Py_ssize_t cache_rate;
    route_input** inputs;
    Py_ssize_t inputs_size;
    PyObject* client_errors[28];
    PyObject* server_errors[11];
    PyObject* exceptions;
    bool has_body;
    bool is_http;

    // transport attributes
    map* routes;
    route* r;
};

route* route_new(
    PyObject* callable,
    Py_ssize_t inputs_size,
    Py_ssize_t cache_rate,
    bool has_body
);
route* route_transport_new(route* r);

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
void route_free(route* r);
int send_raw_text(
    PyObject* awaitable,
    PyObject* send,
    int status,
    const char* res_str,
    PyObject* headers     /* may be NULL */
);

#endif
