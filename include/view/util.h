#ifndef VIEW_UTIL_H
#define VIEW_UTIL_H

#include <Python.h> // PyObject

void _ViewUtil_Fatal(
    const char *message,
    const char *where,
    const char *func,
    int lineno
);

#if defined(__LINE__) && defined(__FILE__)
#define View_FatalError(msg) _ViewUtil_Fatal(msg, __FILE__, __func__, __LINE__)
#else
#define View_FatalError(msg) _ViewUtil_Fatal(msg, "<unknown>.c", __func__, 0)
#endif

#ifdef __GNUC__
#define NORETURN __attribute__((noreturn))
#else
#define NORETURN __declspec(noreturn)
#endif


// Optimization hints, only supported on GCC
#ifdef __GNUC__
#define View_HOT __attribute__((hot)) // Called often
#define View_PURE __attribute__((pure)) // Depends only on input and memory state (i.e. makes no memory allocations)
#define View_CONST __attribute__((const)) // Depends only on inputs
#define View_COLD __attribute__((cold)) // Called rarely
#else
#define View_HOT
#define View_PURE
#define View_CONST
#define View_COLD
#endif

char * ViewUtil_Strdup(const char *c, Py_ssize_t size);
PyObject * ViewUtil_BuildDefaultHeaders();

#endif
