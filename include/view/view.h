#ifndef VIEW_H
#define VIEW_H

#include <Python.h> // PyObject

void view_fatal(
    const char* message,
    const char* where,
    const char* func,
    int lineno
);

extern PyObject* ip_address;
extern PyObject* invalid_status_error;
extern PyObject* route_log;
extern PyObject* route_warn;
extern PyObject* ws_cls;
extern PyObject* ws_disconnect_err;
extern PyObject* ws_err_cls;
extern PyObject* default_headers;

#if defined(__LINE__) && defined(__FILE__)
#define VIEW_FATAL(msg) view_fatal(msg, __FILE__, __func__, __LINE__)
#else
#define VIEW_FATAL(msg) fail(msg, "<unknown>.c", __func__, 0)
#endif

#ifdef __GNUC__
#define NORETURN __attribute__((noreturn))
#else
#define NORETURN __declspec(noreturn)
#endif

#endif
