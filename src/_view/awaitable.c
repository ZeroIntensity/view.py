/* *INDENT-OFF* */
/*
    Proposed implementation for an awaitable C API.
    See https://discuss.python.org/t/adding-a-c-api-for-coroutines-awaitables/22786

    Modified for the purpose of view.py.

    Follows PEP 7, not the _view style.
*/
#include "Python.h"
#include <view/awaitable.h>
#include <stdarg.h>
#include <stdbool.h>

typedef struct {
    PyObject *coro;
    awaitcallback callback;
    awaitcallback_err err_callback;
    bool done;
} awaitable_callback;

struct _PyAwaitableObject {
    PyObject_HEAD
    awaitable_callback **aw_callbacks;
    Py_ssize_t aw_callback_size;
    PyObject *aw_result;
    PyObject *aw_done;
    PyObject *aw_gen;
    PyObject **aw_values;
    Py_ssize_t aw_values_size;
    void **aw_arb_values;
    Py_ssize_t aw_arb_values_size;
};

PyDoc_STRVAR(awaitable_doc,
    "Awaitable transport utility for the C API.");

static PyObject *
awaitable_new(PyTypeObject *tp, PyObject *args, PyObject *kwds)
{
    assert(tp != NULL);
    assert(tp->tp_alloc != NULL);

    PyObject *self = tp->tp_alloc(tp, 0);
    if (self == NULL) {
        return NULL;
    }

    PyAwaitableObject *aw = (PyAwaitableObject *) self;
    aw->aw_callbacks = NULL;
    aw->aw_callback_size = 0;
    aw->aw_result = NULL;
    aw->aw_done = Py_NewRef(Py_False);
    aw->aw_gen = NULL;
    aw->aw_values = NULL;
    aw->aw_values_size = 0;

    return (PyObject *) aw;
}

typedef struct {
    PyObject_HEAD
    PyObject **gw_array;
    Py_ssize_t gw_size;
    Py_ssize_t gw_index;
    PyObject *gw_result;
} GenWrapperObject;

static PyObject *
gen_new(PyTypeObject *tp, PyObject *args, PyObject *kwds)
{
    assert(tp != NULL);
    assert(tp->tp_alloc != NULL);

    PyObject *self = tp->tp_alloc(tp, 0);
    if (self == NULL) {
        return NULL;
    }

    GenWrapperObject *g = (GenWrapperObject *) self;
    g->gw_array = NULL;
    g->gw_size = 0;
    g->gw_index = 0;
    g->gw_result = NULL;

    return (PyObject *) g;
}

static void
gen_dealloc(PyObject *self)
{
    GenWrapperObject *g = (GenWrapperObject *) self;
    Py_XDECREF(g->gw_result);
    for (int i = 0; i < g->gw_size; i++) {
        PyObject *item = g->gw_array[i];
        Py_DECREF(item);
    }
    if (g->gw_array) PyMem_Free(g->gw_array);
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
_PyAwaitable_GenWrapper_New()
{
    GenWrapperObject *g = (GenWrapperObject *) gen_new(
        &_PyAwaitable_GenWrapper_Type,
        NULL,
        NULL
    );

    if (!g) return NULL;
    return (PyObject *) g;
}

static void
_PyAwaitable_GenWrapper_SetResult(PyObject *gen, PyObject *result)
{
    assert(gen != NULL);
    assert(result != NULL);
    Py_INCREF(gen);
    GenWrapperObject *g = (GenWrapperObject *) gen;

    g->gw_result = Py_NewRef(result);
    Py_DECREF(gen);
}

static PyObject *
gen_next(PyObject *self)
{
    GenWrapperObject *g = (GenWrapperObject *) self;

    if (g->gw_array == NULL) {
        PyErr_SetString(PyExc_ValueError, "_GenWrapper has no values");
        return NULL;
    }

    if (g->gw_size == g->gw_index) {
        if (g->gw_result == NULL) {
            PyErr_SetObject(PyExc_StopIteration, Py_NewRef(Py_None));
        } else {
            PyErr_SetObject(PyExc_StopIteration, Py_NewRef(g->gw_result));
        }

        return NULL;
    }

    return g->gw_array[g->gw_index++];
}

static int
gen_add(PyObject *self, PyObject *value)
{
    assert(value != NULL);
    Py_INCREF(value);
    Py_INCREF(self);
    GenWrapperObject *g = (GenWrapperObject *) self;

    ++g->gw_size;
    if (g->gw_array == NULL) {
        g->gw_array = PyMem_Calloc(g->gw_size,
        sizeof(PyObject *));
    } else {
        g->gw_array = PyMem_Realloc(g->gw_array,
        sizeof(PyObject *) * g->gw_size
    );
    }

    if (g->gw_array == NULL) {
        --g->gw_array;
        Py_DECREF(self);
        Py_DECREF(value);
        PyErr_NoMemory();
        return -1;
    }

    g->gw_array[g->gw_size - 1] = value;
    return 0;
}

static int
fire_err_callback(PyObject *self, PyObject *await, awaitable_callback *cb)
{
    if (!cb->err_callback) {
        cb->done = true;
        Py_DECREF(cb->coro);
        Py_XDECREF(await);
        return -1;
    }
    PyObject *res_type, *res_value, *res_traceback;
    PyErr_Fetch(&res_type, &res_value, &res_traceback);
    Py_INCREF(self);
    int e_res = cb->err_callback(self, res_type, res_value, res_traceback);
    Py_DECREF(self);
    PyErr_Restore(res_type, res_value, res_traceback);

    if (e_res < 0) {
        cb->done = true;
        Py_DECREF(cb->coro);
        Py_XDECREF(await);
        return -1;
    };

    PyErr_Clear();
    return 0;
}

static PyObject *
awaitable_next(PyObject *self)
{
    PyAwaitableObject *aw = (PyAwaitableObject *) self;

    if (Py_IsTrue(aw->aw_done)) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "cannot reuse already awaited object"
        );
        return NULL;
    }
    PyObject *gen = _PyAwaitable_GenWrapper_New();

    if (gen == NULL)
        return NULL;

    aw->aw_gen = Py_NewRef(gen);
    assert(aw->aw_callbacks != NULL);
    gen_add(gen, Py_NewRef(Py_None));

    for (int i = 0; i < aw->aw_callback_size; ++i) {
        awaitable_callback *cb = aw->aw_callbacks[i];
        unaryfunc am_await = Py_TYPE(cb->coro)->tp_as_async ?
            Py_TYPE(cb->coro)->tp_as_async->am_await :
            NULL;
        if (am_await == NULL) {
            PyErr_Format(PyExc_TypeError, "%R has no __await__", cb->coro);
            return NULL;
        } 
        PyObject *await = am_await(cb->coro);
        if (await == NULL) {
            if (fire_err_callback(self, await, cb) < 0)
                return NULL;
            return gen;
        }
        Py_INCREF(await);

        PyObject *item = NULL;
        while (1) {
            item = Py_TYPE(await)->tp_iternext(await);
            if (item == NULL) {
                PyObject *occurred = PyErr_Occurred();
                if (
                    !occurred ||
                    PyErr_GivenExceptionMatches(occurred, PyExc_StopIteration)
                ) {
                    if (cb->callback == NULL) break;
                    PyObject *type, *value, *traceback;
                    PyErr_Fetch(&type, &value, &traceback);
                    if (value == NULL) {
                        Py_INCREF(Py_None);
                        value = Py_None;
                    } else {
                        if (PyObject_IsInstance(value, PyExc_StopIteration)) {
                            value = PyObject_GetAttrString(value, "value");
                            if (!value) return NULL;
                        }
                    }
                    Py_INCREF(value);
                    Py_INCREF(self);
                    int result = cb->callback(self, value);
                    Py_DECREF(self);
                    Py_DECREF(value);
                    if (result < 0) {
                        if (fire_err_callback(self, await, cb) < 0)
                            return NULL;
                    }
                    break;
                }
                cb->done = true;
                if (fire_err_callback(self, await, cb) < 0)
                    return NULL;
                break;
            }
        }

        Py_DECREF(await);
        Py_DECREF(cb->coro);
        cb->done = true;
    }

    return gen;
}

static void
awaitable_dealloc(PyObject *self)
{
    PyAwaitableObject *aw = (PyAwaitableObject *) self;
    if (aw->aw_values) {
        for (int i = 0; i < aw->aw_values_size; i++)
            Py_DECREF(aw->aw_values[i]);
        PyMem_Free(aw->aw_values);
    }

    Py_XDECREF(aw->aw_gen);
    Py_XDECREF(aw->aw_result);
    Py_DECREF(aw->aw_done);

    for (int i = 0; i < aw->aw_callback_size; i++) {
        awaitable_callback *cb = aw->aw_callbacks[i];
        if (!cb->done) Py_DECREF(cb->coro);
        PyMem_Free(cb);
    }

    if (aw->aw_arb_values) PyMem_Free(aw->aw_arb_values);
    Py_TYPE(self)->tp_free(self);
}

static PyObject *
awaitable_repr(PyObject *self) {
    assert(self != NULL);
    PyAwaitableObject *aw = (PyAwaitableObject *) self;
    Py_ssize_t done_size = 0;
    for (int i = 0; i < aw->aw_callback_size; i++) {
        if (aw->aw_callbacks[i]->done) ++done_size;
    }
    return PyUnicode_FromFormat("<builtin awaitable, %zd done of %zd>",
                                done_size, aw->aw_callback_size);
}

static PyAsyncMethods async_methods = {
    .am_await = awaitable_next
};

PyTypeObject _PyAwaitable_GenWrapper_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "_GenWrapper", 
    sizeof(GenWrapperObject),
    0,
    gen_dealloc,                                /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    PyDoc_STR(""),                              /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    gen_next,                                   /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    gen_new,                                    /* tp_new */
};

PyTypeObject PyAwaitable_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "awaitable",
    sizeof(PyAwaitableObject),
    0,
    awaitable_dealloc,                          /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    &async_methods,                             /* tp_as_async */
    awaitable_repr,                             /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                         /* tp_flags */
    awaitable_doc,                              /* tp_doc */
    0,                                          /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    awaitable_next,                             /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    awaitable_new,                              /* tp_new */
};

void
PyAwaitable_ClearAwaits(PyObject *aw)
{
    assert(aw != NULL);
    Py_INCREF(aw);

    PyAwaitableObject *a = (PyAwaitableObject *) aw;

    for (int i = 0; i < a->aw_callback_size; i++) {
        awaitable_callback* cb = a->aw_callbacks[i];
        if (!cb->done)
            Py_DECREF(cb->coro);
    }

    Py_DECREF(aw);
}

int
PyAwaitable_AddAwait(
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

    awaitable_callback* aw_c = PyMem_Malloc(sizeof(awaitable_callback));
    if (aw_c == NULL) {
        Py_DECREF(aw);
        Py_DECREF(coro);
        PyErr_NoMemory();
        return -1;
    }

    ++a->aw_callback_size;
    if (a->aw_callbacks == NULL) {
        a->aw_callbacks = PyMem_Calloc(a->aw_callback_size,
        sizeof(awaitable_callback *));
    } else {
        a->aw_callbacks = PyMem_Realloc(a->aw_callbacks,
        sizeof(awaitable_callback *) * a->aw_callback_size
    );
    }

    if (a->aw_callbacks == NULL) {
        --a->aw_callbacks;
        Py_DECREF(aw);
        Py_DECREF(coro);
        PyMem_Free(aw_c);
        PyErr_NoMemory();
        return -1;
    }

    aw_c->coro = coro; // steal our own reference
    aw_c->callback = cb;
    aw_c->err_callback = err;
    a->aw_callbacks[a->aw_callback_size - 1] = aw_c;
    Py_DECREF(aw);

    return 0;
}

int
PyAwaitable_SetResult(PyObject *awaitable, PyObject *result)
{
    assert(awaitable != NULL);
    assert(result != NULL);
    Py_INCREF(result);
    Py_INCREF(awaitable);

    PyAwaitableObject *aw = (PyAwaitableObject *) awaitable;
    if (aw->aw_gen == NULL) {
        PyErr_SetString(PyExc_TypeError, "no generator is currently present");
        Py_DECREF(awaitable);
        Py_DECREF(result);
        return -1;
    }
    _PyAwaitable_GenWrapper_SetResult(aw->aw_gen, result);
    Py_DECREF(awaitable);
    Py_DECREF(result);
    return 0;
}

int
PyAwaitable_UnpackValues(PyObject *awaitable, ...) {
    assert(awaitable != NULL);
    PyAwaitableObject *aw = (PyAwaitableObject *) awaitable;
    Py_INCREF(awaitable);

    if (aw->aw_values == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "awaitable object has no stored values");
        Py_DECREF(awaitable);
        return -1;
    }

    va_list args;
    va_start(args, awaitable);

    for (int i = 0; i < aw->aw_values_size; i++) {
        PyObject **ptr = va_arg(args, PyObject **);
        if (ptr == NULL) continue;
        *ptr = aw->aw_values[i];
        // borrowed reference
    }

    va_end(args);
    Py_DECREF(awaitable);
    return 0;
}

int
PyAwaitable_SaveValues(PyObject *awaitable, Py_ssize_t nargs, ...) {
    assert(awaitable != NULL);
    assert(nargs != 0);
    Py_INCREF(awaitable);
    PyAwaitableObject *aw = (PyAwaitableObject *) awaitable;

    va_list vargs;
    va_start(vargs, nargs);
    int offset = aw->aw_values_size;

    if (aw->aw_values == NULL)
        aw->aw_values = PyMem_Calloc(
            nargs,
            sizeof(PyObject *)
        );
    else
        aw->aw_values = PyMem_Realloc(
            aw->aw_values,
            sizeof(PyObject *) * (aw->aw_values_size + nargs)
        );

    if (aw->aw_values == NULL) {
        PyErr_NoMemory();
        Py_DECREF(awaitable);
        return -1;
    }

    aw->aw_values_size += nargs;

    for (int i = offset; i < aw->aw_values_size; i++)
        aw->aw_values[i] = Py_NewRef(va_arg(vargs, PyObject*));

    va_end(vargs);
    Py_DECREF(awaitable);
    return 0;
}

int
PyAwaitable_UnpackArbValues(PyObject *awaitable, ...) {
    assert(awaitable != NULL);
    PyAwaitableObject *aw = (PyAwaitableObject *) awaitable;
    Py_INCREF(awaitable);

    if (aw->aw_values == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "awaitable object has no stored arbitrary values");
        Py_DECREF(awaitable);
        return -1;
    }

    va_list args;
    va_start(args, awaitable);

    for (int i = 0; i < aw->aw_arb_values_size; i++) {
        void **ptr = va_arg(args, void **);
        if (ptr == NULL) continue;
        *ptr = aw->aw_arb_values[i];
    }

    va_end(args);
    Py_DECREF(awaitable);
    return 0;
}

int
PyAwaitable_SaveArbValues(PyObject *awaitable, Py_ssize_t nargs, ...) {
    assert(awaitable != NULL);
    assert(nargs != 0);
    Py_INCREF(awaitable);
    PyAwaitableObject *aw = (PyAwaitableObject *) awaitable;

    va_list vargs;
    va_start(vargs, nargs);
    int offset = aw->aw_arb_values_size;

    if (aw->aw_arb_values == NULL)
        aw->aw_arb_values = PyMem_Calloc(
            nargs,
            sizeof(void *)
        );
    else
        aw->aw_arb_values = PyMem_Realloc(
            aw->aw_arb_values,
            sizeof(void *) * (aw->aw_arb_values_size + nargs)
        );

    if (aw->aw_arb_values == NULL) {
        PyErr_NoMemory();
        Py_DECREF(awaitable);
        return -1;
    }

    aw->aw_arb_values_size += nargs;

    for (int i = offset; i < aw->aw_arb_values_size; i++)
        aw->aw_arb_values[i] = va_arg(vargs, void *);

    va_end(vargs);
    Py_DECREF(awaitable);
    return 0;
}

PyObject *
PyAwaitable_New()
{
    PyObject *aw = awaitable_new(&PyAwaitable_Type, NULL, NULL);
    return aw;
}
