#ifndef VIEW_H
#define VIEW_H

#include <view/backport.h>
#include <view/app.h>
#include <view/awaitable.h>
#include <view/map.h>


void view_fatal(
    const char* message,
    const char* where,
    const char* func,
    int lineno
);

#if defined(__LINE__) && defined(__FILE__)
#define VIEW_FATAL(msg) view_fatal(msg, __FILE__, __func__, __LINE__)
#else
#define VIEW_FATAL(msg) fail(msg, "<unknown>.c", __func__, 0)
#endif

#endif
