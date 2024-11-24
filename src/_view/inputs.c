/*
 * view.py route inputs implementation
 *
 * This file is responsible for parsing route inputs through query
 * strings and body parameters.
 *
 * If a route has no inputs, then the parsing
 * step is skipped for optimization purposes.
 *
 * If a route has only query inputs, then we don't need to go through the
 * body parsing step, and only parse the query string (handle_route_query()).
 *
 * If a route has body inputs, then we start by parsing that, and if it has any
 * query string parameters, that's handled later. ASGI does not send the body
 * in a single receive() call, so we have a buffer that increases over time.
 *
 * This implementation is also in charge of building data inputs (such as Context() or WebSocket())
 * and appending them to routes. This is indicated by a special integer determined by the loader.
 *
 */
#include <Python.h>
#include <stdbool.h>
#include <pyawaitable.h>

#include <view/util.h>
