/*
 * Path parts implementation (aka path parameters).
 *
 * This is unfinished, undocumented, and quite buggy.
 * Nearly all of this will be changed or rewritten.
 *
 * The underlying implementation is quite complicated, so let's try and go through
 * it with an example.
 *
 * Let's say the requested route is GET /app/12345/index and 12345 is a path parameter.
 *
 * We would first call map_get(app->get, "/app"). Of this returns NULL, it is a 404.
 * Then, we map_get(route->routes, "/12345"). If NULL, then we check if a route->r is available.
 *
 * If so, this is a path parameter, we save the value and move on to the next. Otherwise, 404.
 * We repeat this process until we reach the end of the URL. So, next we do map_get(route->r->routes, "/index").
 *
 * Once again, we check if map_get(route->r->routes, "/index") is NULL. If it isn't, then we check
 * if route->r->r is non-NULL. If it is, then it's a 404. Otherwise, once again save the value as a path parameter
 * and repeat the process.
 *
 * This will go until the end of the path is reached.
 *
 * In the above example, then order of operations would look like so:
 *
 * - app_routes["/app/12345/index"] -> NULL, check for path parameters.
 * - app_routes["/app"] -> non-NULL, proceed with path parameter extraction.
 * - app_routes["/app"].routes["/12345"] -> NULL, check if transport is available.
 * - app_routes["/app"].r -> non-NULL, this is a path parameter! If not, a 404 would be sent back.
 * - path_params = ["12345"]
 * - app_routes["/app"].r.routes["/index"] -> non-NULL, proceed.
 * - Reached end of path! Location of our route object is app_routes["/app"].r.routes["/index"],
 *   with ["12345"] as the initial inputs.
 *
 * A visual representation of the route structure could look like such:
 *
 * This is our initial route, which
 * is only accessed if, in this case,
 * /app/12345/index returns NULL.
 * +-- /app --+
 * |          |
 * |   ...    |                           This is the object we want!
 * |          |                           +-- /index --+
 * |   routes -------> NULL               |            |
 * |   r ------------> +----------+       |     ...    |
 * |          |        |          |       |            |
 * +----------+        |   NULL   |       |     routes ------> NULL
 *                     |          |       |     r -----------> NULL
 *                     |          |       |            |
 *                     |  routes -------> +------------+
 *                     |  r ------------> NULL
 *                     |          |
 *                     +----------+
 *                     This is our transport
 *                     route, it represents
 *                     a path parameter.
 */
#include <Python.h>
#include <stdbool.h> // true

#include <view/app.h> // ViewApp
#include <view/errors.h>
#include <view/map.h> // map
#include <view/route.h> // route, route_free
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

/*
 * The implementation of runtime path parameter extraction.
 *
 * This is extremely buggy - do not use this function.
 */
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

/*
 * Generate route tables on routes, and add transport routes.
 *
 * This is a one-time cost, so performance is not super important
 * in this function.
 *
 * Private API - subject to change.
 */
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
