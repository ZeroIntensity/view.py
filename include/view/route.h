#ifndef VIEW_ROUTE_H
#define VIEW_ROUTE_H

#include <stdint.h> // uint16_t

#include <view/app.h>
#include <view/array.h>
#include <view/map.h>
#include <view/util.h> // View_AllocStructureCast

typedef struct _route ViewRoute;
typedef struct _response ViewResponse;

typedef struct _result
{
    PyObject *return_value;
    char *response_body;
    int status_code;
    PyObject *headers;
} ViewRoute_Result;

#define ViewRoute_New() View_AllocStructureCast(ViewRoute)
void ViewRoute_Free(ViewRoute *r);

PyObject *
ViewRoute_GetFunction(ViewRoute *route);

int
ViewRoute_Result_ToResponse(
    PyObject *raw_result,
    ViewResponse *response
);

#endif
