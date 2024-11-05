#include <Python.h>

#include <view/util.h>

/*
 * Crash Python and view.py with a fatal error.
 *
 * Don't use this directly! Use the VIEW_FATAL macro instead.
 */
View_NORETURN void
_View_Fatal(
    const char *message,
    View_Where *where
)
{
    fprintf(
        stderr,
        "_view FATAL ERROR at [%s:%d] in %s: %s\n",
        where->file,
        where->line_number,
        where->function_name,
        message
    );
    fputs(
        "Please report this at https://github.com/ZeroIntensity/view.py/issues\n",
        stderr
    );
    Py_FatalError("view.py core died");
};


/*
 * Implementation of strdup() using PyMem_Malloc()
 *
 * Unlike strdup(), this takes a size parameter. Try
 * to avoid using strlen(), and use a function that includes
 * the string size, such as PyUnicode_AsUTF8AndSize()
 *
 * Strings that are returned by this function should
 * be freed using PyMem_Free(), not free()
 *
 * Technically speaking, this is more or less a copy
 * of CPython's private _PyMem_Strdup function.
 */
char *
View_Strdup(const char *c, Py_ssize_t size)
{
    char *buf = PyMem_Malloc(size + 1); // Length with null terminator
    if (View_UNLIKELY(buf == NULL))
        return (char *) PyErr_NoMemory();
    memcpy(buf, c, size + 1);
    return buf;
}

void *
View_AllocStructure(Py_ssize_t size)
{
    void *ptr = PyMem_Calloc(1, size);
    if (View_UNLIKELY(ptr == NULL))
    {
        return PyErr_NoMemory();
    }

    return ptr;
}
