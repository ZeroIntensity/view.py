/* *INDENT-OFF* */
#ifndef VIEW_AWAITABLE_H
#define VIEW_AWAITABLE_H

#include <Python.h>
#include <view/backport.h>

typedef int (*awaitcallback)(PyObject *, PyObject *);
typedef int (*awaitcallback_err)(PyObject *, PyObject *, PyObject *, PyObject *);

typedef struct _PyAwaitableObject PyAwaitableObject;

extern PyTypeObject PyAwaitable_Type;
extern PyTypeObject _PyAwaitable_GenWrapper_Type;

PyObject *PyAwaitable_New();

int PyAwaitable_AddAwait(PyObject *aw, PyObject *coro, awaitcallback cb, awaitcallback_err err);
void PyAwaitable_Cancel(PyObject *aw);

int PyAwaitable_SetResult(PyObject *awaitable, PyObject *result);

int PyAwaitable_SaveValues(PyObject *awaitable, Py_ssize_t nargs, ...);
int PyAwaitable_UnpackValues(PyObject *awaitable, ...);

int PyAwaitable_SaveArbValues(PyObject *awaitable, Py_ssize_t nargs, ...);
void PyAwaitable_SetArbValue(PyObject *awaitable, Py_ssize_t index, void *ptr);
int PyAwaitable_UnpackArbValues(PyObject *awaitable, ...);

#define PyAwaitable_AWAIT(aw, coro) PyAwaitable_AddAwait(aw, coro, NULL, NULL)

int PyAwaitable_SaveIntValues(PyObject *awaitable, Py_ssize_t nargs, ...);
int PyAwaitable_UnpackIntValues(PyObject *awaitable, ...);

#endif
