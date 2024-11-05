#ifndef VIEW_ROUTE_H
#define VIEW_ROUTE_H

#include <stdint.h> // uint16_t

#include <view/app.h>
#include <view/array.h>
#include <view/map.h>
#include <view/inputs.h>

typedef struct _ViewRoute ViewRoute;

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

struct _ViewRoute
{
    PyObject *route_callable;
    ViewRoute_Cache cache;
    ViewArray inputs;
    ViewApp_ErrorState errors;
    ViewRoute_Flags flags;
};

void ViewRoute_Free(ViewRoute *r);
ViewRoute * ViewRoute_New();
ViewRoute * ViewRoute_NewTransport(ViewRoute *r);

#endif
