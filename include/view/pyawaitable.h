/*
 * Modified version of PyAwaitable
 * See https://github.com/ZeroIntensity/pyawaitable
 */
#ifndef PYAWAITABLE_VENDOR_H
#define PYAWAITABLE_VENDOR_H

#include <Python.h>
#include <stdbool.h>
#include <stdlib.h>

typedef int (*awaitcallback)(PyObject *, PyObject *);
typedef int (*awaitcallback_err)(
    PyObject *,
    PyObject *
);

#define CALLBACK_ARRAY_SIZE 128
#define VALUE_ARRAY_SIZE 32

typedef struct _pyawaitable_callback
{
    PyObject *coro;
    awaitcallback callback;
    awaitcallback_err err_callback;
    bool done;
} pyawaitable_callback;

struct _PyAwaitableObject
{
    PyObject_HEAD

    // Callbacks
    pyawaitable_callback *aw_callbacks[CALLBACK_ARRAY_SIZE];
    Py_ssize_t aw_callback_index;

    // Stored Values
    PyObject *aw_values[VALUE_ARRAY_SIZE];
    Py_ssize_t aw_values_index;

    // Arbitrary Values
    void *aw_arb_values[VALUE_ARRAY_SIZE];
    Py_ssize_t aw_arb_values_index;

    // Integer Values
    int aw_int_values[VALUE_ARRAY_SIZE];
    Py_ssize_t aw_int_values_index;

    // Awaitable State
    Py_ssize_t aw_state;
    bool aw_done;
    bool aw_awaited;
    bool aw_used;

    // Misc
    PyObject *aw_result;
    PyObject *aw_gen;
};

typedef struct _PyAwaitableObject PyAwaitableObject;
extern PyTypeObject _PyAwaitableType;

int pyawaitable_set_result(PyObject *awaitable, PyObject *result);

int pyawaitable_await(
    PyObject *aw,
    PyObject *coro,
    awaitcallback cb,
    awaitcallback_err err
);

void pyawaitable_cancel(PyObject *aw);

PyObject *
awaitable_next(PyObject *self);

PyObject *
pyawaitable_new(void);

int
pyawaitable_await_function(
    PyObject *awaitable,
    PyObject *func,
    const char *fmt,
    awaitcallback cb,
    awaitcallback_err err,
    ...
);

int
alloc_awaitable_pool(void);
void
dealloc_awaitable_pool(void);


PyObject *pyawaitable_new(void);

int pyawaitable_save_arb(PyObject *awaitable, Py_ssize_t nargs, ...);

int pyawaitable_unpack_arb(PyObject *awaitable, ...);

int pyawaitable_save(PyObject *awaitable, Py_ssize_t nargs, ...);

int pyawaitable_unpack(PyObject *awaitable, ...);

int
pyawaitable_save_int(PyObject *awaitable, Py_ssize_t nargs, ...);

int pyawaitable_unpack_int(PyObject *awaitable, ...);


#ifndef _PyObject_Vectorcall
#define PYAWAITABLE_NEEDS_VECTORCALL
PyObject *_PyObject_VectorcallBackport(
    PyObject *obj,
    PyObject **args,
    size_t nargsf,
    PyObject *kwargs
);

#define PyObject_CallNoArgs(o) PyObject_CallObject(o, NULL)
#define PyObject_Vectorcall _PyObject_VectorcallBackport
#define PyObject_VectorcallDict _PyObject_FastCallDict
#endif

#if PY_VERSION_HEX < 0x030c0000
PyObject *PyErr_GetRaisedException(void);
void PyErr_SetRaisedException(PyObject *err);
#endif

#ifndef Py_NewRef
#define PYAWAITABLE_NEEDS_NEWREF
PyObject *Py_NewRef_Backport(PyObject *o);
#define Py_NewRef Py_NewRef_Backport
#endif

#ifndef Py_XNewRef
#define PYAWAITABLE_NEEDS_XNEWREF
PyObject *Py_XNewRef_Backport(PyObject *o);
#define Py_XNewRef Py_XNewRef_Backport
#endif


extern PyMethodDef pyawaitable_methods[];
extern PyAsyncMethods pyawaitable_async_methods;


extern PyTypeObject _PyAwaitableGenWrapperType;

typedef struct _GenWrapperObject
{
    PyObject_HEAD
    PyAwaitableObject *gw_aw;
    PyObject *gw_current_await;
} GenWrapperObject;

PyObject *
genwrapper_next(PyObject *self);

int genwrapper_fire_err_callback(
    PyObject *self,
    PyObject *await,
    pyawaitable_callback *cb
);

PyObject *
genwrapper_new(PyAwaitableObject *aw);


/*
 * vendor.h is only for use by the vendor build tool, don't use it manually!
 * (If you're seeing this message from a vendored copy, you're fine)
 */

#define PYAWAITABLE_ADD_TYPE(m, tp)                                 \
        do                                                          \
        {                                                           \
            Py_INCREF(&tp);                                         \
            if (PyType_Ready(&tp) < 0) {                            \
                Py_DECREF(&tp);                                     \
                return -1;                                          \
            }                                                       \
            if (PyModule_AddObject(m, #tp, (PyObject *) &tp) < 0) { \
                Py_DECREF(&tp);                                     \
                return -1;                                          \
            }                                                       \
        } while (0)

#define PYAWAITABLE_MAJOR_VERSION 1
#define PYAWAITABLE_MINOR_VERSION 0
#define PYAWAITABLE_MICRO_VERSION 0
#define PYAWAITABLE_RELEASE_LEVEL 0xF

#define PyAwaitable_New pyawaitable_new
#define PyAwaitable_AddAwait pyawaitable_await
#define PyAwaitable_Cancel pyawaitable_cancel
#define PyAwaitable_SetResult pyawaitable_set_result
#define PyAwaitable_SaveValues pyawaitable_save
#define PyAwaitable_SaveArbValues pyawaitable_save_arb
#define PyAwaitable_SaveIntValues pyawaitable_save_int
#define PyAwaitable_UnpackValues pyawaitable_unpack
#define PyAwaitable_UnpackArbValues pyawaitable_unpack_arb
#define PyAwaitable_UnpackIntValues pyawaitable_unpack_int
#define PyAwaitable_Init pyawaitable_init
#define PyAwaitable_ABI pyawaitable_abi
#define PyAwaitable_Type PyAwaitableType
#define PyAwaitable_AwaitFunction pyawaitable_await_function
#define PyAwaitable_VendorInit pyawaitable_vendor_init
#define PyAwaitable_AWAIT(aw, coro) pyawaitable_await(aw, coro, NULL, NULL)
#define PyAwaitable_SetArbValue(awaitable, index,                          \
                                value) ((PyAwaitableObject *) awaitable)-> \
        aw_arb_values[index] = value;

static int
pyawaitable_init()
{
    PyErr_SetString(
        PyExc_SystemError,
        "cannot use pyawaitable_init from a vendored copy, use pyawaitable_vendor_init instead!"
    );
    return -1;
}

static void
close_pool(PyObject *Py_UNUSED(capsule))
{
    dealloc_awaitable_pool();
}

static int
pyawaitable_vendor_init(PyObject *mod)
{
    PYAWAITABLE_ADD_TYPE(mod, _PyAwaitableType);
    PYAWAITABLE_ADD_TYPE(mod, _PyAwaitableGenWrapperType);

    PyObject *capsule = PyCapsule_New(
        pyawaitable_vendor_init, // Any pointer, except NULL
        "_pyawaitable.__do_not_touch",
        close_pool
    );

    if (!capsule)
    {
        return -1;
    }

    if (PyModule_AddObject(mod, "__do_not_touch", capsule) < 0)
    {
        Py_DECREF(capsule);
        return -1;
    }

    if (alloc_awaitable_pool() < 0)
    {
        return -1;
    }

    return 0;
}

#endif
