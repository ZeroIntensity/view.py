/*
 * PyAwaitable - Vendored copy of version 1.0.0 (modified for the purpose of view.py)
 *
 * Docs: https://awaitable.zintensity.dev
 * Source: https://github.com/ZeroIntensity/pyawaitable
 */

#include <view/backport.h>
#include <view/pyawaitable.h>
#include <view/view.h> // HOT

PyTypeObject _PyAwaitableGenWrapperType; // Forward declaration
/* Vendor of src/_pyawaitable/genwrapper.c */


static PyObject *
gen_new(PyTypeObject *tp, PyObject *args, PyObject *kwds)
{
    assert(tp != NULL);
    assert(tp->tp_alloc != NULL);

    PyObject *self = tp->tp_alloc(tp, 0);
    if (self == NULL)
    {
        return NULL;
    }

    GenWrapperObject *g = (GenWrapperObject *) self;
    g->gw_aw = NULL;
    g->gw_current_await = NULL;

    return (PyObject *) g;
}

static void
gen_dealloc(PyObject *self)
{
    GenWrapperObject *g = (GenWrapperObject *) self;
    Py_XDECREF(g->gw_current_await);
    Py_XDECREF(g->gw_aw);
    Py_TYPE(self)->tp_free(self);
}

PyObject *
genwrapper_new(PyAwaitableObject *aw)
{
    assert(aw != NULL);
    GenWrapperObject *g = (GenWrapperObject *) gen_new(
        &_PyAwaitableGenWrapperType,
        NULL,
        NULL
    );

    if (!g)
        return NULL;

    g->gw_aw = (PyAwaitableObject *) Py_NewRef((PyObject *) aw);
    return (PyObject *) g;
}

int
genwrapper_fire_err_callback(
    PyObject *self,
    PyObject *await,
    pyawaitable_callback *cb
)
{
    assert(PyErr_Occurred() != NULL);
    if (!cb->err_callback)
    {
        cb->done = true;
        Py_DECREF(cb->coro);
        Py_XDECREF(await);
        return -1;
    }

    Py_INCREF(self);
    PyObject *err = PyErr_GetRaisedException();
    int e_res = cb->err_callback(self, err);
    cb->done = true;
    Py_DECREF(self);

    if (e_res < 0)
    {
        // If the res is -1, the error is restored.
        // Otherwise, it is not.
        if (e_res == -1)
        {
            PyErr_SetRaisedException(err);
        } else
        {
            Py_DECREF(err);
        }

        Py_DECREF(cb->coro);
        Py_XDECREF(await);
        return -1;
    }

    Py_XDECREF(await);
    Py_DECREF(err);
    return 0;
}

PyObject *
genwrapper_next(PyObject *self)
{
    GenWrapperObject *g = (GenWrapperObject *) self;
    PyAwaitableObject *aw = g->gw_aw;

    if (!aw)
    {
        PyErr_SetString(
            PyExc_SystemError,
            "pyawaitable: genwrapper used after return"
        );
        return NULL;
    }

    pyawaitable_callback *cb;
    if (aw->aw_state == CALLBACK_ARRAY_SIZE)
    {
        PyErr_SetString(
            PyExc_SystemError,
            "pyawaitable: object cannot handle more than 255 coroutines"
        );
        return NULL;
    }

    if (g->gw_current_await == NULL)
    {
        if (aw->aw_callbacks[aw->aw_state] == NULL)
        {
            aw->aw_done = true;
            PyErr_SetObject(
                PyExc_StopIteration,
                aw->aw_result ? aw->aw_result : Py_None
            );
            Py_DECREF(g->gw_aw);
            g->gw_aw = NULL;
            return NULL;
        }

        cb = aw->aw_callbacks[aw->aw_state++];

        if (
            Py_TYPE(cb->coro)->tp_as_async == NULL ||
            Py_TYPE(cb->coro)->tp_as_async->am_await == NULL
        )
        {
            PyErr_Format(
                PyExc_TypeError,
                "pyawaitable: %R has no __await__",
                cb->coro
            );
            return NULL;
        }

        g->gw_current_await = Py_TYPE(cb->coro)->tp_as_async->am_await(
            cb->coro
        );
        if (g->gw_current_await == NULL)
        {
            if (
                genwrapper_fire_err_callback(
                    (PyObject *) aw,
                    g->gw_current_await,
                    cb
                ) < 0
            )
            {
                return NULL;
            }

            return genwrapper_next(self);
        }
    } else
    {
        cb = aw->aw_callbacks[aw->aw_state - 1];
    }

    PyObject *result = Py_TYPE(
        g->gw_current_await
    )->tp_iternext(g->gw_current_await);

    if (result == NULL)
    {
        PyObject *occurred = PyErr_Occurred();
        if (!occurred)
        {
            // Coro is done
            if (!cb->callback)
            {
                Py_DECREF(g->gw_current_await);
                g->gw_current_await = NULL;
                return genwrapper_next(self);
            }
        }

        if (
            occurred && !PyErr_GivenExceptionMatches(
                occurred,
                PyExc_StopIteration
            )
        )
        {
            if (
                genwrapper_fire_err_callback(
                    (PyObject *) aw,
                    g->gw_current_await,
                    cb
                ) < 0
            )
            {
                g->gw_current_await = NULL;
                return NULL;
            }
            g->gw_current_await = NULL;
            return genwrapper_next(self);
        }

        if (cb->callback == NULL)
        {
            // Coroutine is done, but with a result.
            // We can disregard the result if theres no callback.
            Py_DECREF(g->gw_current_await);
            g->gw_current_await = NULL;
            PyErr_Clear();
            return genwrapper_next(self);
        }

        PyObject *value;
        if (occurred)
        {
            PyObject *type, *traceback;
            PyErr_Fetch(&type, &value, &traceback);
            PyErr_NormalizeException(&type, &value, &traceback);
            Py_XDECREF(type);
            Py_XDECREF(traceback);

            if (value == NULL)
            {
                value = Py_NewRef(Py_None);
            } else
            {
                assert(PyObject_IsInstance(value, PyExc_StopIteration));
                PyObject *tmp = PyObject_GetAttrString(value, "value");
                if (tmp == NULL)
                {
                    Py_DECREF(value);
                    return NULL;
                }
                value = tmp;
            }
        } else
        {
            value = Py_NewRef(Py_None);
        }

        Py_INCREF(aw);
        int result = cb->callback((PyObject *) aw, value);
        Py_DECREF(aw);
        Py_DECREF(value);

        if (result < -1)
        {
            // -2 or lower denotes that the error should be deferred,
            // regardless of whether a handler is present.
            return NULL;
        }

        if (result < 0)
        {
            if (!PyErr_Occurred())
            {
                PyErr_SetString(
                    PyExc_SystemError,
                    "pyawaitable: callback returned -1 without exception set"
                );
                return NULL;
            }
            if (
                genwrapper_fire_err_callback(
                    (PyObject *) aw,
                    g->gw_current_await,
                    cb
                ) < 0
            )
            {
                g->gw_current_await = NULL;
                return NULL;
            }
        }

        cb->done = true;
        g->gw_current_await = NULL;
        return genwrapper_next(self);
    }

    return result;
}

PyTypeObject _PyAwaitableGenWrapperType =
{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_genwrapper",
    .tp_basicsize = sizeof(GenWrapperObject),
    .tp_dealloc = gen_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_iter = PyObject_SelfIter,
    .tp_iternext = genwrapper_next,
    .tp_new = gen_new,
};
/* Vendor of src/_pyawaitable/coro.c */

static PyObject *
awaitable_send_with_arg(PyObject *self, PyObject *value)
{
    PyAwaitableObject *aw = (PyAwaitableObject *) self;
    if (aw->aw_gen == NULL)
    {
        PyObject *gen = awaitable_next(self);
        if (gen == NULL)
            return NULL;

        Py_RETURN_NONE;
    }

    return genwrapper_next(aw->aw_gen);
}

static PyObject *
awaitable_send(PyObject *self, PyObject *args)
{
    PyObject *value;

    if (!PyArg_ParseTuple(args, "O", &value))
        return NULL;

    return awaitable_send_with_arg(self, value);
}

static PyObject *
awaitable_close(PyObject *self, PyObject *args)
{
    pyawaitable_cancel(self);
    PyAwaitableObject *aw = (PyAwaitableObject *) self;
    aw->aw_done = true;
    Py_RETURN_NONE;
}

static PyObject *
awaitable_throw(PyObject *self, PyObject *args)
{
    PyObject *type;
    PyObject *value = NULL;
    PyObject *traceback = NULL;

    if (!PyArg_ParseTuple(args, "O|OO", &type, &value, &traceback))
        return NULL;

    if (PyType_Check(type))
    {
        PyObject *err = PyObject_Vectorcall(
            type,
            (PyObject *[]) { value },
            1,
            NULL
        );
        if (err == NULL)
        {
            return NULL;
        }

        if (traceback)
            if (PyException_SetTraceback(err, traceback) < 0)
            {
                Py_DECREF(err);
                return NULL;
            }

        PyErr_Restore(err, NULL, NULL);
    } else
        PyErr_Restore(
            Py_NewRef(type),
            Py_XNewRef(value),
            Py_XNewRef(traceback)
        );

    PyAwaitableObject *aw = (PyAwaitableObject *)self;
    if ((aw->aw_gen != NULL) && (aw->aw_state != 0))
    {
        GenWrapperObject *gw = (GenWrapperObject *)aw->aw_gen;
        pyawaitable_callback *cb = aw->aw_callbacks[aw->aw_state - 1];
        if (cb == NULL)
            return NULL;

        if (genwrapper_fire_err_callback(self, gw->gw_current_await, cb) < 0)
        {
            gw->gw_current_await = NULL;
            return NULL;
        }
    } else
        return NULL;

    assert(NULL);
}

#if PY_MINOR_VERSION > 9
static PySendResult
awaitable_am_send(PyObject *self, PyObject *arg, PyObject **presult)
{
    PyObject *send_res = awaitable_send_with_arg(self, arg);
    if (send_res == NULL)
    {
        PyObject *occurred = PyErr_Occurred();
        if (PyErr_GivenExceptionMatches(occurred, PyExc_StopIteration))
        {
            PyObject *item = PyObject_GetAttrString(occurred, "value");

            if (item == NULL)
            {
                return PYGEN_ERROR;
            }

            *presult = item;
            return PYGEN_RETURN;
        }
        *presult = NULL;
        return PYGEN_ERROR;
    }
    PyAwaitableObject *aw = (PyAwaitableObject *)self;
    *presult = send_res;

    return PYGEN_NEXT;
}

#endif

PyMethodDef pyawaitable_methods[] =
{
    {"send", awaitable_send, METH_VARARGS, NULL},
    {"close", awaitable_close, METH_VARARGS, NULL},
    {"throw", awaitable_throw, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

PyAsyncMethods pyawaitable_async_methods =
{
#if PY_MINOR_VERSION > 9
    .am_await = awaitable_next,
    .am_send = awaitable_am_send
#else
    .am_await = awaitable_next
#endif
};
/* Vendor of src/_pyawaitable/values.c */
#define UNPACK(arr, tp, err, index)                                  \
        do {                                                         \
            assert(awaitable != NULL);                               \
            PyAwaitableObject *aw = (PyAwaitableObject *) awaitable; \
            Py_INCREF(awaitable);                                    \
            va_list args;                                            \
            va_start(args, awaitable);                               \
            for (int i = 0; i < index; ++i) {                        \
                tp ptr = va_arg(args, tp);                           \
                if (ptr == NULL)                                     \
                continue;                                            \
                *ptr = arr[i];                                       \
            }                                                        \
            va_end(args);                                            \
            Py_DECREF(awaitable);                                    \
            return 0;                                                \
        } while (0)

#define SAVE_ERR(err)                                     \
        "pyawaitable: " err " array has a capacity of 32" \
        ", so storing %ld more would overflow it"         \

#define SAVE(arr, index, tp, err, wrap)                              \
        do {                                                         \
            assert(awaitable != NULL);                               \
            assert(nargs != 0);                                      \
            Py_INCREF(awaitable);                                    \
            PyAwaitableObject *aw = (PyAwaitableObject *) awaitable; \
            Py_ssize_t final_size = index + nargs;                   \
            if (final_size >= VALUE_ARRAY_SIZE) {                    \
                PyErr_Format(                                        \
    PyExc_SystemError,                                               \
    SAVE_ERR(err),                                                   \
    final_size                                                       \
                );                                                   \
                return -1;                                           \
            }                                                        \
            va_list vargs;                                           \
            va_start(vargs, nargs);                                  \
            for (Py_ssize_t i = index; i < final_size; ++i) {        \
                arr[i] = wrap(va_arg(vargs, tp));                    \
            }                                                        \
            index += nargs;                                          \
            va_end(vargs);                                           \
            Py_DECREF(awaitable);                                    \
            return 0;                                                \
        } while (0)

#define NOTHING

/* Normal Values */

int
pyawaitable_unpack(PyObject *awaitable, ...)
{
    UNPACK(aw->aw_values, PyObject * *, "values", aw->aw_values_index);
}

int
pyawaitable_save(PyObject *awaitable, Py_ssize_t nargs, ...)
{
    SAVE(aw->aw_values, aw->aw_values_index, PyObject *, "values", Py_NewRef);
}

/* Arbitrary Values */

int
pyawaitable_unpack_arb(PyObject *awaitable, ...)
{
    UNPACK(
        aw->aw_arb_values,
        void **,
        "arbitrary values",
        aw->aw_arb_values_index
    );
}

int
pyawaitable_save_arb(PyObject *awaitable, Py_ssize_t nargs, ...)
{
    SAVE(
        aw->aw_arb_values,
        aw->aw_arb_values_index,
        void *,
        "arbitrary values",
        NOTHING
    );
}

/* Integer Values */

int
pyawaitable_unpack_int(PyObject *awaitable, ...)
{
    UNPACK(
        aw->aw_int_values,
        int *,
        "integer values",
        aw->aw_int_values_index
    );
}

int
pyawaitable_save_int(PyObject *awaitable, Py_ssize_t nargs, ...)
{
    SAVE(
        aw->aw_int_values,
        aw->aw_int_values_index,
        int,
        "integer values",
        NOTHING
    );
}

/* Vendor of src/_pyawaitable/awaitable.c */
#define AWAITABLE_POOL_SIZE 256

PyDoc_STRVAR(
    awaitable_doc,
    "Awaitable transport utility for the C API."
);

static Py_ssize_t pool_index = 0;
static PyObject *pool[AWAITABLE_POOL_SIZE];

static PyObject *
awaitable_new_func(PyTypeObject *tp, PyObject *args, PyObject *kwds)
{
    assert(tp != NULL);
    assert(tp->tp_alloc != NULL);

    PyObject *self = tp->tp_alloc(tp, 0);
    if (self == NULL)
    {
        return NULL;
    }

    PyAwaitableObject *aw = (PyAwaitableObject *) self;
    aw->aw_awaited = false;
    aw->aw_done = false;
    aw->aw_used = false;

    return (PyObject *) aw;
}

PyObject *
awaitable_next(PyObject *self)
{
    PyAwaitableObject *aw = (PyAwaitableObject *)self;
    aw->aw_awaited = true;

    if (aw->aw_done)
    {
        PyErr_SetString(
            PyExc_RuntimeError,
            "pyawaitable: cannot reuse awaitable"
        );
        return NULL;
    }

    PyObject *gen = genwrapper_new(aw);

    if (gen == NULL)
    {
        return NULL;
    }

    aw->aw_gen = gen;
    return Py_NewRef(gen);
}

static void
awaitable_dealloc(PyObject *self)
{
    PyAwaitableObject *aw = (PyAwaitableObject *) self;
    for (int i = 0; i < aw->aw_values_index; ++i)
    {
        Py_DECREF(aw->aw_values[i]);
    }

    Py_XDECREF(aw->aw_gen);
    Py_XDECREF(aw->aw_result);

    for (int i = 0; i < aw->aw_callback_index; ++i)
    {
        pyawaitable_callback *cb = aw->aw_callbacks[i];

        if (!cb->done)
            Py_DECREF(cb->coro);
        PyMem_Free(cb);
    }

    if (!aw->aw_done && aw->aw_used)
    {
        if (
            PyErr_WarnEx(
                PyExc_RuntimeWarning,
                "pyawaitable object was never awaited",
                1
            ) < 0
        )
        {
            PyErr_WriteUnraisable(self);
        }
    }

    Py_TYPE(self)->tp_free(self);
}

void
pyawaitable_cancel(PyObject *aw)
{
    assert(aw != NULL);
    Py_INCREF(aw);

    PyAwaitableObject *a = (PyAwaitableObject *) aw;

    for (int i = 0; i < CALLBACK_ARRAY_SIZE; ++i)
    {
        pyawaitable_callback *cb = a->aw_callbacks[i];
        if (!cb)
            break;

        if (!cb->done)
            Py_DECREF(cb->coro);

        a->aw_callbacks[i] = NULL;
    }

    Py_DECREF(aw);
}

int
pyawaitable_await(
    PyObject *aw,
    PyObject *coro,
    awaitcallback cb,
    awaitcallback_err err
)
{
    assert(aw != NULL);
    assert(coro != NULL);
    Py_INCREF(coro);
    Py_INCREF(aw);
    PyAwaitableObject *a = (PyAwaitableObject *) aw;
    if (a->aw_callback_index == CALLBACK_ARRAY_SIZE)
    {
        PyErr_SetString(
            PyExc_SystemError,
            "pyawaitable: awaitable object cannot store more than 128 coroutines"
        );
        return -1;
    }

    pyawaitable_callback *aw_c = PyMem_Malloc(sizeof(pyawaitable_callback));
    if (aw_c == NULL)
    {
        Py_DECREF(aw);
        Py_DECREF(coro);
        PyErr_NoMemory();
        return -1;
    }

    aw_c->coro = coro; // Steal our own reference
    aw_c->callback = cb;
    aw_c->err_callback = err;
    aw_c->done = false;
    a->aw_callbacks[a->aw_callback_index++] = aw_c;
    Py_DECREF(aw);

    return 0;
}

int
pyawaitable_set_result(PyObject *awaitable, PyObject *result)
{
    assert(awaitable != NULL);
    assert(result != NULL);

    PyAwaitableObject *aw = (PyAwaitableObject *) awaitable;
    aw->aw_result = Py_NewRef(result);
    return 0;
}

PyObject *
pyawaitable_new(void)
{
    if (pool_index == AWAITABLE_POOL_SIZE)
    {
        PyObject *aw = awaitable_new_func(&_PyAwaitableType, NULL, NULL);
        ((PyAwaitableObject *) aw)->aw_used = true;
        return aw;
    }

    PyObject *pool_obj = pool[pool_index++];
    ((PyAwaitableObject *) pool_obj)->aw_used = true;
    return pool_obj;
}

void
dealloc_awaitable_pool(void)
{
    for (Py_ssize_t i = pool_index; i < AWAITABLE_POOL_SIZE; ++i)
    {
        if (Py_REFCNT(pool[i]) != 1)
        {
            PyErr_Format(
                PyExc_SystemError,
                "expected %R to have a reference count of 1",
                pool[i]
            );
            PyErr_WriteUnraisable(NULL);
        }
        Py_DECREF(pool[i]);
    }
}

int
alloc_awaitable_pool(void)
{
    for (Py_ssize_t i = 0; i < AWAITABLE_POOL_SIZE; ++i)
    {
        pool[i] = awaitable_new_func(&_PyAwaitableType, NULL, NULL);
        if (!pool[i])
        {
            for (Py_ssize_t x = 0; x < i; ++x)
                Py_DECREF(pool[x]);
            return -1;
        }
    }

    return 0;
}

int
pyawaitable_await_function(
    PyObject *awaitable,
    PyObject *func,
    const char *fmt,
    awaitcallback cb,
    awaitcallback_err err,
    ...
)
{
    size_t len = strlen(fmt);
    size_t size = len + 3;
    char *tup_format = PyMem_Malloc(size);
    if (!tup_format)
    {
        PyErr_NoMemory();
        return -1;
    }

    tup_format[0] = '(';
    for (size_t i = 0; i < len; ++i)
    {
        tup_format[i + 1] = fmt[i];
    }

    tup_format[size - 2] = ')';
    tup_format[size - 1] = '\0';

    va_list vargs;
    va_start(vargs, err);
    PyObject *args = Py_VaBuildValue(tup_format, vargs);
    va_end(vargs);
    PyMem_Free(tup_format);

    if (!args)
        return -1;
    PyObject *coro = PyObject_Call(func, args, NULL);
    Py_DECREF(args);

    if (!coro)
        return -1;

    if (pyawaitable_await(awaitable, coro, cb, err) < 0)
    {
        Py_DECREF(coro);
        return -1;
    }

    Py_DECREF(coro);
    return 0;
}

PyTypeObject _PyAwaitableType =
{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_PyAwaitableType",
    .tp_basicsize = sizeof(PyAwaitableObject),
    .tp_dealloc = awaitable_dealloc,
    .tp_as_async = &pyawaitable_async_methods,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = awaitable_doc,
    .tp_iternext = awaitable_next,
    .tp_new = awaitable_new_func,
    .tp_methods = pyawaitable_methods
};
