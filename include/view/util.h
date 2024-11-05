#ifndef VIEW_UTIL_H
#define VIEW_UTIL_H

#include <Python.h> // PyObject

typedef struct _where
{
    const char *file;
    const char *function_name;
    int line_number;
} View_Where;

#if defined(__LINE__) && defined(__FILE__)
#define View_HERE()                                                 \
        (View_Where)({ .file = __FILE__, .function_name = __func__, \
                       .line_number = __LINE__})
#else
#define View_HERE()                               \
        (View_Where)({ .file = "<unknown>.c",     \
                       .function_name = __func__, \
                       .line_number = 0 })
#endif

void _View_Fatal(const char *message, View_Where *where);
#define View_Fatal(message)                        \
        do {                                       \
            _View_Where _where_here = View_HERE(); \
            _View_Fatal(message, &_where_here);    \
        } while (0)

#ifdef __GNUC__
#define View_NORETURN __attribute__((noreturn))
#else
#define View_NORETURN __declspec(noreturn)
#endif


// Optimization hints, only supported on GCC
#ifdef __GNUC__
#define View_HOT __attribute__((hot)) // Called often
#define View_PURE __attribute__((pure)) // Depends only on input and memory state (i.e. makes no memory allocations)
#define View_CONST __attribute__((const)) // Depends only on inputs
#define View_COLD __attribute__((cold)) // Called rarely

#define View_LIKELY(expr) __builtin_expect((expr), 1)
#define View_UNLIKELY(expr) __builtin_expect((expr), 0)
#else
#define View_HOT
#define View_PURE
#define View_CONST
#define View_COLD

#define View_LIKELY(expr) (expr)
#define View_UNLIKELY(expr) (expr)
#endif

char * View_Strdup(const char *c, Py_ssize_t size);
PyObject * View_BuildDefaultHeaders();
void *View_AllocStructure(Py_ssize_t size);

#define View_AllocStructureCast(tp) ((tp *)View_AllocStructure(sizeof(tp)))

#endif
