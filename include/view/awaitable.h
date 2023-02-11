#ifndef VIEW_AWAITABLE_H
#define VIEW_AWAITABLE_H

#include <Python.h>

typedef struct _PyAwaitableObject PyAwaitableObject;
typedef int (*awaitcallback)(PyObject *, PyObject *);

PyObject *PyAwaitable_New();

int PyAwaitable_SetResult(PyObject *awaitable, PyObject *result);
int PyAwaitable_AddAwait(PyObject *aw, PyObject *coro, awaitcallback cb);
extern PyTypeObject PyAwaitable_Type;
extern PyTypeObject _PyAwaitable_GenWrapper_Type;
PyObject *PyAwaitable_GetValue(PyObject *awaitable);
int PyAwaitable_SaveValues(PyObject *awaitable, Py_ssize_t nargs, ...);
int PyAwaitable_UnpackValues(PyObject *awaitable, ...);
int PyAwaitable_SaveValue(PyObject *awaitable, const void *value);

#endif
