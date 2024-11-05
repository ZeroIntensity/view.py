#ifndef VIEW_ARRAY_H
#define VIEW_ARRAY_H

#include <Python.h>

#define ViewArray_DEFAULT_SIZE 16

/*
 * Deallocator for items on a ViewArray structure. A NULL pointer
 * will never be given to the deallocator.
 */
typedef void (*ViewArray_Deallocator)(void *);

/*
 * Internal only dynamic array for CPython.
 */
typedef struct
{
    /*
     * The actual items in the dynamic array.
     * Don't access this field publicly to get
     * items--use ViewArray_GET_ITEM() instead.
     */
    void **items;
    /*
     * The length of the actual items array allocation.
     */
    Py_ssize_t capacity;
    /*
     * The number of items in the array.
     * Don't use this field publicly--use ViewArray_LENGTH()
     */
    Py_ssize_t length;
    /*
     * The deallocator, set by one of the initializer functions.
     * This may be NULL.
     */
    ViewArray_Deallocator deallocator;
} ViewArray;


static inline void
ViewArray_ASSERT_VALID(ViewArray *array)
{
    assert(array != NULL);
    assert(array->items != NULL);
}

static inline void
ViewArray_ASSERT_INDEX(ViewArray *array, Py_ssize_t index)
{
    // Ensure the index is valid
    assert(index >= 0);
    assert(index < array->length);
}

/*
 * Initialize a dynamic array with an initial size and deallocator.
 *
 * If the deallocator is NULL, then nothing happens to items upon
 * removal and upon array clearing.
 *
 * Returns -1 upon failure, 0 otherwise.
 */
PyAPI_FUNC(int)
ViewArray_InitWithSize(
    ViewArray * array,
    ViewArray_Deallocator deallocator,
    Py_ssize_t initial
);

/*
 * Append to the array.
 *
 * Returns -1 upon failure, 0 otherwise.
 * If this fails, the deallocator is not ran on the item.
 */
PyAPI_FUNC(int) ViewArray_Append(ViewArray * array, void *item);

/*
 * Insert an item at the target index. The index
 * must currently be a valid index in the array.
 *
 * Returns -1 upon failure, 0 otherwise.
 * If this fails, the deallocator is not ran on the item.
 */
PyAPI_FUNC(int)
ViewArray_Insert(ViewArray * array, Py_ssize_t index, void *item);


/*
 * Clear all the fields on the array.
 *
 * Note that this does *not* free the actual dynamic array
 * structure--use ViewArray_Free() for that.
 *
 * It's safe to call ViewArray_Init() or InitWithSize() again
 * on the array after calling this.
 */
PyAPI_FUNC(void) ViewArray_Clear(ViewArray * array);

/*
 * Set a value at index in the array.
 *
 * If an item already exists at the target index, the deallocator
 * is called on it, if the array has one set.
 *
 * This cannot fail.
 */
PyAPI_FUNC(void)
ViewArray_Set(ViewArray * array, Py_ssize_t index, void *item);

/*
 * Remove the item at the index, and call the deallocator on it (if the array
 * has one set).
 *
 * This cannot fail.
 */
PyAPI_FUNC(void)
ViewArray_Remove(ViewArray * array, Py_ssize_t index);

/*
 * Remove the item at the index *without* deallocating it, and
 * return the item.
 *
 * This cannot fail.
 */
PyAPI_FUNC(void *)
ViewArray_Pop(ViewArray * array, Py_ssize_t index);

/*
 * Clear all the fields on a dynamic array, and then
 * free the dynamic array structure itself.
 *
 * The array must have been created by ViewArray_New()
 */
static inline void
ViewArray_Free(ViewArray *array)
{
    ViewArray_ASSERT_VALID(array);
    ViewArray_Clear(array);
    PyMem_RawFree(array);
}

/*
 * Equivalent to ViewArray_InitWithSize() with a default size of 16.
 *
 * Returns -1 upon failure, 0 otherwise.
 */
static inline int
ViewArray_Init(ViewArray *array, ViewArray_Deallocator deallocator)
{
    return ViewArray_InitWithSize(
        array,
        deallocator,
        ViewArray_DEFAULT_SIZE
    );
}

/*
 * Allocate and create a new dynamic array on the heap.
 *
 * The returned pointer should be freed with ViewArray_Free()
 * If this function fails, it returns NULL.
 */
static inline ViewArray *
ViewArray_NewWithSize(
    ViewArray_Deallocator deallocator,
    Py_ssize_t initial
)
{
    ViewArray *array = PyMem_RawMalloc(sizeof(ViewArray));
    if (array == NULL)
    {
        return NULL;
    }

    if (ViewArray_InitWithSize(array, deallocator, initial) < 0)
    {
        PyMem_RawFree(array);
        return NULL;
    }

    ViewArray_ASSERT_VALID(array); // Sanity check
    return array;
}

/*
 * Equivalent to ViewArray_NewWithSize() with a size of 16.
 *
 * The returned array must be freed with ViewArray_Free().
 * Returns NULL on failure.
 */
static inline ViewArray *
ViewArray_New(ViewArray_Deallocator deallocator)
{
    return ViewArray_NewWithSize(deallocator, ViewArray_DEFAULT_SIZE);
}

/*
 * Get an item from the array. This cannot fail.
 *
 * If the index is not valid, this is undefined behavior.
 */
static inline void *
ViewArray_GET_ITEM(ViewArray *array, Py_ssize_t index)
{
    ViewArray_ASSERT_VALID(array);
    ViewArray_ASSERT_INDEX(array, index);
    return array->items[index];
}

/*
 * Get the length of the array. This cannot fail.
 */
static inline Py_ssize_t
ViewArray_LENGTH(ViewArray *array)
{
    ViewArray_ASSERT_VALID(array);
    return array->length;
}

/*
 * Pop the item at the end the array.
 * This function cannot fail.
 */
static inline void *
ViewArray_PopTop(ViewArray *array)
{
    return ViewArray_Pop(array, ViewArray_LENGTH(array) - 1);
}

#endif
