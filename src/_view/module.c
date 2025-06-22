#include <Python.h>
#include <pyawaitable.h>

static int _view_exec(PyObject *mod)
{
    return PyAwaitable_Init();
}

static PyMethodDef _view_methods[] = {
    {NULL}
};

static PyModuleDef_Slot _view_slots[] = {
    {Py_mod_exec, _view_exec},
    {0, NULL}
};

static PyModuleDef _view_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_view",
    .m_methods = _view_methods,
    .m_slots = _view_slots
};

PyMODINIT_FUNC
PyInit__view(void)
{
    return PyModuleDef_Init(&_view_module);
}
