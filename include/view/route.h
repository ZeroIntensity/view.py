#ifndef VIEW_ROUTE_H
#define VIEW_ROUTE_H

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

void route_free(route* r);
route* route_new(
    PyObject* callable,
    Py_ssize_t inputs_size,
    Py_ssize_t cache_rate,
    bool has_body
);
route* route_transport_new(route* r);

#endif
