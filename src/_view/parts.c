#include <Python.h>
#include <stdbool.h> // true

#include <view/app.h> // ViewApp
#include <view/errors.h>
#include <view/map.h> // map
#include <view/routing.h> // route
#include <view/view.h> // VIEW_FATAL

#define TRANSPORT_MAP() map_new(2, (map_free_func) route_free)

// Port of strsep for use on windows
char* v_strsep(char** stringp, const char* delim) {
    char* rv = *stringp;
    if (rv) {
        *stringp += strcspn(
            *stringp,
            delim
        );
        if (**stringp)
            *(*stringp)++ = '\0';
        else
            *stringp = 0;
    }
    return rv;
}

int extract_parts(
    ViewApp* self,
    PyObject* awaitable,
    map* target,
    char* path,
    const char* method_str,
    Py_ssize_t* size,
    route** out_r,
    PyObject*** out_params
) {
    char* token;
    route* rt = NULL;
    bool did_save = false;
    PyObject** params = calloc(
        1,
        sizeof(PyObject*)
    );
    if (!params) {
        PyErr_NoMemory();
        return -1;
    }

    bool skip = true; // skip leading /
    route* last_r = NULL;

    while ((token = v_strsep(
        &path,
        "/"
                    ))) {
        if (skip) {
            skip = false;
            continue;
        }
        // TODO: optimize this
        char* s = PyMem_Malloc(strlen(token) + 2);
        sprintf(
            s,
            "/%s",
            token
        );
        assert(target);

        if ((!did_save && rt && rt->r) || last_r) {
            printf(
                "last_r: %p\n",
                last_r
            );
            route* this_r = (last_r ? last_r : rt)->r;
            last_r = this_r;

            PyObject* unicode = PyUnicode_FromString(token);
            if (!unicode) {
                for (int i = 0; i < *size; i++)
                    Py_DECREF(params[i]);

                PyMem_Free(params);
                return -1;
            }

            params = realloc(
                params,
                (++(*size)) * sizeof(PyObject*)
            );
            params[*size - 1] = unicode;
            if (this_r->routes) target = this_r->routes;
            if (!this_r->r) last_r = NULL;
            did_save = true; // prevent this code from looping, but also preserve rt in case the iteration ends
            continue;
        } else if (did_save) did_save = false;

        rt = map_get(
            target,
            s
        );
        PyMem_Free(s);

        if (!rt) {
            // the route doesnt exist!
            for (int i = 0; i < *size; i++)
                Py_DECREF(params[i]);

            PyMem_Free(params);
            if (fire_error(
                self,
                awaitable,
                404,
                NULL,
                NULL,
                NULL,
                method_str,
                true
                ) < 0) {
                Py_DECREF(awaitable);
                return -1;
            }

            return -2;
        }

        target = rt->routes;
    }

    bool failed = false;
    route* r = rt->r;
    if (r && !r->callable) {
        r = r->r; // edge case
        if (!r) failed = true;
    } else if (!r) failed = true;

    if (failed) {
        for (int i = 0; i < *size; i++)
            Py_DECREF(params[i]);

        PyMem_Free(params);
        if (fire_error(
            self,
            awaitable,
            404,
            NULL,
            NULL,
            NULL,
            method_str,
            true
            ) < 0) {
            return -1;
        }

        return -2;
    }
}

int load_parts(ViewApp* app, map* routes, PyObject* parts, route* r) {
    PyObject* iter = PyObject_GetIter(parts);
    if (!iter) return -1;

    PyObject* item;
    map* target = routes;
    route* rt = NULL;
    Py_ssize_t size = PySequence_Size(parts);
    if (size == -1) {
        Py_DECREF(iter);
        return -1;
    }

    Py_ssize_t index = 0;
    bool set_r = false;

    while ((item = PyIter_Next(iter))) {
        ++index;

        if (PyUnicode_CheckExact(
            item
            )) {
            // path part
            const char* str = PyUnicode_AsUTF8(item);
            if (!str) {
                Py_DECREF(iter);
                return -1;
            };
            route* found = map_get(
                target,
                str
            );
            route* transport = route_transport_new(NULL);
            if (!transport) {
                Py_DECREF(iter);
                return -1;
            };
            if (!found) {
                map_set(
                    target,
                    str,
                    transport
                );
                transport->routes = TRANSPORT_MAP();
                target = transport->routes;
                if (!target) {
                    Py_DECREF(iter);
                    return -1;
                };
            } else {
                if (!found->routes) found->routes = TRANSPORT_MAP();
                if (!found->routes) {
                    Py_DECREF(iter);
                    return -1;
                };
                target = found->routes;
                map_set(
                    target,
                    str,
                    transport
                );
            }
            rt = transport;
        } else {
            app->has_path_params = true;
            if (!rt) VIEW_FATAL("first path param was part");
            if (index == size) {
                rt->r = r;
                set_r = true;
            } else {
                rt->r = route_transport_new(NULL);
                rt = rt->r;
            }
        }
        if (!set_r) rt->r = r;
    }

    Py_DECREF(iter);
    if (PyErr_Occurred()) return -1;

    return 0;
}
