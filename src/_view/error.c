#include <view/view.h>
#include <Python.h>

typedef struct {
    PyObject_HEAD;
} Error;

static void dealloc(Error* self) {
    puts("deallocating");
}

static PyObject* init(Error* self, PyObject* args, PyObject* kwargs) {
    puts("init");
    Py_RETURN_NONE;
}

static PyObject* new(PyTypeObject* type, PyObject* args, PyObject* kwargs) {
    puts("a");
    Error* self = (Error*) type->tp_alloc(type, 0);
    if (!self)
        return NULL;

    return (PyObject*) self;
}


static PyMethodDef methods[] = {
    //{"_compile", (PyCFunction) compile, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};


PyTypeObject ErrorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_view._Error",
    .tp_basicsize = sizeof(Error),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_dealloc = (destructor) dealloc,
    //.tp_methods = methods,
    //.tp_init = (initproc) init
};
