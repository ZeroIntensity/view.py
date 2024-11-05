/*
 * view.py internal route implementation
 *
 * This file contains the allocators and deallocator for route structures.
 *
 * Note that technically speaking, there are two types of routes: standard and transport.
 * In the current state, every route is a standard route. However, the unstable and buggy
 * path parameter API uses transport routes to represent path parameters. Read the comment
 * at the top of parts.c for how that works.
 *
 * Standard routes are initialized with route_new(), while transports are
 * initialized with route_transport_new()
 *
 * Essentially, standard route instances hold all proper route fields, except the
 * "routes" and "r" fields. Both of these are NULL in a standard route.
 *
 * In a transport, it's the opposite - everything is NULL except "routes" and "r".
 *
 * Standard routes are responsible for managing the memory of all of their fields.
 * However, the inputs array is not allocated by route_new() - that's done by the loader.
 * The route_free() deallocator expects that the inputs array has been allocated.
 *
 * With that being said, expect everything from typecodes to reference counts to be
 * managed by a route pointer.
 */
#include <Python.h>

#include <view/route.h>
#include <view/response.h> // ViewResponse

typedef struct _cache_state
{
    ViewResponse *response;
    Py_ssize_t rate;
    Py_ssize_t index;
} ViewRoute_Cache;

typedef enum _route_flags
{
    HAS_BODY = 1 << 0,
    IS_HTTP = 1 << 1,
} ViewRoute_Flags;

struct _route
{
    PyObject *route_callable;
    ViewRoute_Cache cache;
    ViewArray inputs;
    ViewApp_ErrorState errors;
    ViewRoute_Flags flags;
};

static void
clear_cache(ViewRoute_Cache *cache)
{
    if (cache->response == NULL)
    {
        // Nothing to clear
        return;
    }
    Py_XDECREF(cache->response->headers_list);
}

void
ViewRoute_Free(ViewRoute *r)
{
    ViewArray_Clear(&r->inputs);
    clear_cache(&r->cache);
    ViewApp_ClearErrorState(&r->errors);
    PyMem_Free(r);
}

PyObject *
ViewRoute_GetFunction(ViewRoute *route)
{
    assert(route != NULL);
    assert(route->route_callable != NULL);
    assert(PyCallable_Check(route->route_callable));
    return Py_NewRef(route->route_callable);
}
