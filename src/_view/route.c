/*
 * view.py route implementation.
 *
 * This file contains the allocators and deallocator for route structures.
 */
#include <Python.h>
#include <view/route.h>

/*
 * Allocator for routes.
 *
 * This function does not allocate the inputs array, regardless
 * of the `inputs_size` parameter.
 *
 * If this fails, a MemoryError is raised.
 */
route* route_new(
    PyObject* callable,
    Py_ssize_t inputs_size,
    Py_ssize_t cache_rate,
    bool has_body
) {
    route* r = PyMem_Malloc(sizeof(route));
    if (!r)
        return (route*) PyErr_NoMemory();

    r->cache = NULL;
    r->callable = Py_NewRef(callable);
    r->cache_rate = cache_rate;
    r->cache_index = 0;
    r->cache_headers = NULL;
    r->cache_status = 0;
    r->inputs = NULL;
    r->inputs_size = inputs_size;
    r->has_body = has_body;
    r->is_http = true;

    // transports
    r->routes = NULL;
    r->r = NULL;

    for (int i = 0; i < 28; i++)
        r->client_errors[i] = NULL;

    for (int i = 0; i < 11; i++)
        r->server_errors[i] = NULL;

    return r;
}

/*
 * Deallocator for routes.
 *
 * This function assumes that the inputs array has been allocated, and
 * is responsible for deallocating it with PyMem_Free()
 */
void route_free(route* r) {
    for (int i = 0; i < r->inputs_size; i++){
        if (r->inputs[i]->route_data) {
            continue;
        }
        Py_XDECREF(r->inputs[i]->df);
        free_type_codes(
            r->inputs[i]->types,
            r->inputs[i]->types_size
        );

        for (int i = 0; i < r->inputs[i]->validators_size; i++){
            Py_DECREF(r->inputs[i]->validators[i]);
        }
    }

    PyMem_Free(r->inputs);

    Py_XDECREF(r->cache_headers);
    Py_DECREF(r->callable);

    for (int i = 0; i < 11; i++)
        Py_XDECREF(r->server_errors[i]);

    for (int i = 0; i < 28; i++)
        Py_XDECREF(r->client_errors[i]);

    if (r->cache)
        PyMem_Free(r->cache);
    PyMem_Free(r);
}

/*
 * Allocator for a "route transport," per the path parts API.
 *
 * Along with the rest of the path parts API, this function
 * should be considered very buggy and subject to change.
 */
route* route_transport_new(route* r) {
    route* rt = PyMem_Malloc(sizeof(route));
    if (!rt)
        return (route*)PyErr_NoMemory();
    rt->cache = NULL;
    rt->callable = NULL;
    rt->cache_rate = 0;
    rt->cache_index = 0;
    rt->cache_headers = NULL;
    rt->cache_status = 0;
    rt->inputs = NULL;
    rt->inputs_size = 0;
    rt->has_body = false;
    rt->is_http = false;

    for (int i = 0; i < 28; i++)
        rt->client_errors[i] = NULL;

    for (int i = 0; i < 11; i++)
        rt->server_errors[i] = NULL;

    rt->routes = NULL;
    rt->r = r;
    return rt;
}
