/* *INDENT-OFF* */
#ifndef VIEW_AWAITABLE_H
#define VIEW_AWAITABLE_H

#include <Python.h>
#include <view/backport.h>

typedef struct _PyAwaitableObject PyAwaitableObject;
typedef int (*awaitcallback)(PyObject *, PyObject *);
typedef int (*awaitcallback_err)(PyObject *, PyObject *, PyObject *, PyObject *);

PyObject *PyAwaitable_New();

int PyAwaitable_SetResult(PyObject *awaitable, PyObject *result);
int PyAwaitable_AddAwait(PyObject *aw, PyObject *coro, awaitcallback cb, awaitcallback_err err);
extern PyTypeObject PyAwaitable_Type;
extern PyTypeObject _PyAwaitable_GenWrapper_Type;
PyObject *PyAwaitable_GetValue(PyObject *awaitable);
int PyAwaitable_SaveValues(PyObject *awaitable, Py_ssize_t nargs, ...);
int PyAwaitable_UnpackValues(PyObject *awaitable, ...);
int PyAwaitable_UnpackArbValues(PyObject *awaitable, ...);
int PyAwaitable_SaveArbValues(PyObject *awaitable, Py_ssize_t nargs, ...);
int
PyAwaitable_AwaitFunction(PyObject *awaitable, PyObject *function,
                          awaitcallback cb, awaitcallback_err err,
                          const char *format, ...);

#define PyAwaitable_AWAIT(aw, coro) PyAwaitable_AddAwait(aw, coro, NULL, NULL)

#endif
