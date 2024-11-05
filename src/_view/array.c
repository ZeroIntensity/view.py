/*
 * Dynamic array implementation.
 */


#include <view/array.h>

static inline void
call_deallocator_maybe(ViewArray *array, Py_ssize_t index)
{
    if (array->deallocator != NULL && array->items[index] != NULL)
    {
        array->deallocator(array->items[index]);
    }
}

int
ViewArray_InitWithSize(ViewArray *array,
                         ViewArray_Deallocator deallocator,
                         Py_ssize_t initial)
{
    assert(array != NULL);
    assert(initial > 0);
    void **items = PyMem_RawCalloc(sizeof(void *), initial);
    if (items == NULL)
    {
        return -1;
    }

    array->capacity = initial;
    array->items = items;
    array->length = 0;
    array->deallocator = deallocator;

    return 0;
}

static int
resize_if_needed(ViewArray *array)
{
    if (array->length == array->capacity)
    {
        // Need to resize
        array->capacity *= 2;
        void **new_items = PyMem_RawRealloc(
                                            array->items,
                                            sizeof(void *) * array->capacity);
        if (new_items == NULL)
        {
            return -1;
        }

        array->items = new_items;
    }

    return 0;
}

int
ViewArray_Append(ViewArray *array, void *item)
{
    ViewArray_ASSERT_VALID(array);
    array->items[array->length++] = item;
    if (resize_if_needed(array) < 0)
    {
        array->items[--array->length] = NULL;
        return -1;
    }
    return 0;
}

int
ViewArray_Insert(ViewArray *array, Py_ssize_t index, void *item)
{
    ViewArray_ASSERT_VALID(array);
    ViewArray_ASSERT_INDEX(array, index);
    ++array->length;
    if (resize_if_needed(array) < 0)
    {
        // Grow the array beforehand, otherwise it's
        // going to be a mess putting it back together if
        // allocation fails.
        --array->length;
        return -1;
    }

    for (Py_ssize_t i = array->length - 1; i > index; --i)
    {
        array->items[i] = array->items[i - 1];
    }

    array->items[index] = item;
    return 0;
}

void
ViewArray_Set(ViewArray *array, Py_ssize_t index, void *item)
{
    ViewArray_ASSERT_VALID(array);
    ViewArray_ASSERT_INDEX(array, index);
    call_deallocator_maybe(array, index);
    array->items[index] = item;
}

static void
remove_no_dealloc(ViewArray *array, Py_ssize_t index)
{
    for (Py_ssize_t i = index; i < array->length - 1; ++i)
    {
        array->items[i] = array->items[i + 1];
    }
    --array->length;
}

void
ViewArray_Remove(ViewArray *array, Py_ssize_t index)
{
    ViewArray_ASSERT_VALID(array);
    ViewArray_ASSERT_INDEX(array, index);
    call_deallocator_maybe(array, index);
    remove_no_dealloc(array, index);
}

void *
ViewArray_Pop(ViewArray *array, Py_ssize_t index)
{
    ViewArray_ASSERT_VALID(array);
    ViewArray_ASSERT_INDEX(array, index);
    void *item = array->items[index];
    remove_no_dealloc(array, index);
    return item;
}

void
ViewArray_Clear(ViewArray *array)
{
    ViewArray_ASSERT_VALID(array);
    for (Py_ssize_t i = 0; i < array->length; ++i)
    {
        call_deallocator_maybe(array, i);
    }
    PyMem_RawFree(array->items);

    // It would be nice if others could reuse the allocation for another
    // dynarray later, so clear all the fields.
    array->items = NULL;
    array->length = 0;
    array->capacity = 0;
    array->deallocator = NULL;
}