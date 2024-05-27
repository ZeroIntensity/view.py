#include <Python.h>
#include <stdbool.h> // true

#include <view/context.h> // context_from_data
#include <view/ws.h> // ws_from_data
#include <view/parsers.h> // app_parsers
#include <view/inputs.h>
#include <view/typecodes.h>
#include <view/view.h> // VIEW_FATAL

PyObject* build_data_input(
    int num,
    PyObject* scope,
    PyObject* receive,
    PyObject* send
) {
    switch (num) {
    case 1: return context_from_data(scope);
    case 2: return ws_from_data(
        send,
        receive
    );

    default:
        VIEW_FATAL("got invalid route data number");
    }
    return NULL; // to make editor happy
}

PyObject** generate_params(
    app_parsers* parsers,
    const char* data,
    PyObject* query,
    route_input** inputs,
    Py_ssize_t inputs_size,
    PyObject* scope,
    PyObject* receive,
    PyObject* send
) {
    PyObject* py_str = PyUnicode_FromString(data);
    if (!py_str)
        return NULL;

    PyObject* obj = PyObject_Vectorcall(
        parsers->json,
        (PyObject*[]) { py_str },
        1,
        NULL
    );
    Py_DECREF(py_str);

    if (!obj)
        return NULL;

    PyObject** ob = calloc(
        inputs_size,
        sizeof(PyObject*)
    );

    if (!ob) {
        Py_DECREF(obj);
        return NULL;
    }

    for (int i = 0; i < inputs_size; i++) {
        route_input* inp = inputs[i];
        if (inp->route_data) {
            PyObject* data = build_data_input(
                inp->route_data,
                scope,
                receive,
                send
            );
            if (!data) {
                Py_DECREF(obj);
                free(ob);
                return NULL;
            }

            ob[i] = data;
            continue;
        }

        PyObject* raw_item = PyDict_GetItemString(
            inp->is_body ? obj : query,
            inp->name
        );
        PyObject* item = cast_from_typecodes(
            inp->types,
            inp->types_size,
            raw_item,
            parsers->json,
            true
        );

        if (!item) {
            Py_DECREF(obj);
            free(ob);
            return NULL;
        }

        for (int x = 0; x < inp->validators_size; x++) {
            PyObject* o = PyObject_Vectorcall(
                inp->validators[x],
                (PyObject*[]) { item },
                1,
                NULL
            );
            if (!PyObject_IsTrue(o)) {
                Py_DECREF(o);
                free(ob);
                Py_DECREF(obj);
                Py_DECREF(item);
                return NULL;
            }
        }

        ob[i] = item;
    }

    return ob;
}