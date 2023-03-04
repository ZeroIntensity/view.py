#ifndef VIEW_APP_H
#define VIEW_APP_H

#include <Python.h>
#include <view/backport.h>

typedef enum {
    USE_CACHE = 1UL << 1,
    PASS_CTX = 2UL << 2,
} route_flags;

extern PyTypeObject ViewAppType;

#endif
