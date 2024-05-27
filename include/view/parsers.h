#ifndef VIEW_PARSERS_H
#define VIEW_PARSERS_H

typedef struct _app_parsers {
    PyObject* query;
    PyObject* json;
} app_parsers;

int body_inc_buf(PyObject* awaitable, PyObject* result);
int handle_route_query(PyObject* awaitable, char* query);

PyObject* query_parser(
    app_parsers* parsers,
    const char* data
);

#endif