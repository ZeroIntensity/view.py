#include <Python.h>

#include <view/util.h>

/*
 * Crash Python and view.py with a fatal error.
 *
 * Don't use this directly! Use the VIEW_FATAL macro instead.
 */
NORETURN void
view_fatal(
    const char *message,
    const char *where,
    const char *func,
    int lineno
)
{
    fprintf(
        stderr,
        "_view FATAL ERROR at [%s:%d] in %s: %s\n",
        where,
        lineno,
        func,
        message
    );
    fputs(
        "Please report this at https://github.com/ZeroIntensity/view.py/issues\n",
        stderr
    );
    Py_FatalError("view.py core died");
};
