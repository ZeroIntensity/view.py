/*
 * view.py hash map implementation
 *
 * This is a simple and fast hash map that view.py uses instead
 * of Python dictionaries.
 *
 * Maps store an array of pair pointers, which hold two things:
 * - The key as a string, in case there's hash collisions.
 * - The value. This is a void pointer.
 *
 * Maps expand by doubling their capacity every time the limit is reached.
 * The initial capacity is passed to map_new(), and when that is hit, the next
 * call to map_set() will expand the map by a factor of two.
 *
 * For example, if you pass 1 as the initial capacity, the map can hold
 * one item total, and then the next time you call map_set() to add something
 * new, it expands to 2.
 *
 * Now, if you call map_set() a third time, it expands to 4, then 8, then 16, and so on.
 *
 * A map expects that all of the values are the same type, and defers deallocation to
 * the user by letting them pass a deallocator function for each value. This is
 * called on each value upon calling map_free()

 * Upon calling map_get(), the key name is hashed and turned into an index, which
 * is then used to get a value from the pairs array. If the index is NULL, map_get() returns NULL.
 *
 * If it isn't, then we proceed. As one final check, the
 * key passed to the function and the key stored on the pair are checked with strcmp()
 *
 * If they match, great! The value on the pair is returned. If they don't, then there
 * is a hash collision - we need to search the rest of the table. We do this and compare
 * each key on the pair with the one passed. If we find a match, we return it. Otherwise, we
 * return NULL.
 *
 * This implementation uses a Fowler-Noll-Vo hash function to hash strings into integers.
 * Spoiler-alert: this was not home-brewed, nor was most of this implementation!
 * Most of this map implementation is based on other works.
 *
 */
#include <Python.h>
#include <stdint.h> // uint64_t
#include <stdio.h>
#include <string.h> // strdup

#include <view/map.h>
#include <view/results.h> // pymem_strdup
#include <view/view.h> // PURE, COLD

#define FNV_OFFSET 14695981039346656037UL
#define FNV_PRIME 1099511628211UL

/*
 * Fowler-Noll-Vo Hash Function.
 * Read about it here: https://en.wikipedia.org/wiki/Fowler–Noll–Vo_hash_function
 *
 * This function is marked as "pure," meaning it makes no memory allocations, and
 * only depends on the passed parameters and state of memory.
 */
PURE static uint64_t hash_key(const char* key) {
    uint64_t hash = FNV_OFFSET;
    for (const char* p = key; *p; p++) {
        hash ^= (uint64_t) (unsigned char) (*p);
        hash *= FNV_PRIME;
    }
    return hash;
}

/*
 * Get an item out of the map.
 *
 * This hashes the key using an FNV hash function.
 *
 * If the key stored at the index does not matched what was passed to the function,
 * then there is a hash collision, and this function uses an O(n) search to find
 * the value.
 *
 * If no value is found, either by a fast or slow search, this function
 * returns NULL. Note that this does not raise a Python exception.
 *
 * Best case: O(1)
 * Worst case: O(n)
 */
PURE void* map_get(map* m, const char* key) {
    uint64_t hash = hash_key(key);
    Py_ssize_t index = (Py_ssize_t) (hash & (uint64_t)(m->capacity - 1));

    while (m->items[index] != NULL) {
        if (!strcmp(
            key,
            m->items[index]->key
            ))
            return m->items[index]->value;
        index++;
        if (index == m->capacity) {
            index = 0;
            // need to wrap around the table
        }
    }
    return NULL;
}

/*
 * The map initializer and allocator.
 *
 * This allocates an array of size initial_capacity, and
 * stores a function for deallocating values.
 *
 * Note that the deallocator can run before map_free() has
 * been called, as an item will be deallocated if map_set()
 * is called on the same key. For example, if you stored the
 * key "foo" with map_set(), and then stored the key "foo"
 * again later, the original would be deallocated upon setting
 * it again.
 *
 * If this fails, NULL is returned, and a MemoryError
 * is raised.
 */
map* map_new(Py_ssize_t inital_capacity, map_free_func dealloc) {
    map* m = PyMem_Malloc(sizeof(map));
    if (!m)
        return (map*) PyErr_NoMemory();

    m->len = 0;
    m->capacity = inital_capacity;
    m->items = PyMem_Calloc(
        inital_capacity,
        sizeof(pair)
    );
    if (!m->items)
        return (map*) PyErr_NoMemory();
    m->dealloc = dealloc;
    return m;
}

/*
 * Set a pair on a pair array of size `capacity`.
 *
 * If the key is already stored, the value is deallocated
 * with the passed dealloc() function pointer.
 *
 * The `len` parameter is a pointer to a Py_ssize_t, which is incremented
 * if a new entry is created in the pair array.
 *
 * If this function fails, a MemoryError is raised.
 *
 */
static int set_entry(
    pair** items,
    Py_ssize_t capacity,
    const char* key,
    void* value,
    Py_ssize_t* len,
    map_free_func dealloc
) {
    uint64_t hash = hash_key(key);
    Py_ssize_t index = (Py_ssize_t) (hash & (uint64_t)(capacity - 1));

    while (items[index] != NULL) {
        if (!strcmp(
            key,
            items[index]->key
            )) {
            dealloc(items[index]->value);
            items[index]->value = value;
            return 0;
        }

        index++;
        if (index == capacity)
            index = 0;
    }

    if (len != NULL)
        (*len)++;

    if (!items[index]) {
        items[index] = PyMem_Malloc(sizeof(pair));
        if (!items[index]) {
            PyErr_NoMemory();
            return -1;
        }
    }

    char* new_key = pymem_strdup(key, strlen(key));

    if (!new_key) {
        PyMem_Free(items[index]);
        return -1;
    }

    items[index]->key = new_key;
    items[index]->value = value;
    return 0;
}

/*
 * Expand the map's pair array by a factor of two.
 *
 * For example, if the capacity is 4, it will become 8.
 * If it's 8, it will become 16. If it's 16, it will become 32, and so on.
 */
static int expand(map* m) {
    Py_ssize_t new_capacity = m->capacity * 2;
    if (new_capacity < m->capacity) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "integer limit reached on _view map capacity"
        );
        return -1;
    }
    pair** items = PyMem_Calloc(
        new_capacity,
        sizeof(pair)
    );
    if (!items) {
        PyErr_NoMemory();
        return -1;
    }

    for (Py_ssize_t i = 0; i < m->capacity; i++) {
        pair* item = m->items[i];
        if (item) {
            if (set_entry(
                items,
                new_capacity,
                item->key,
                item->value,
                NULL,
                m->dealloc
                ) < 0) {
                return -1;
            };
            PyMem_Free(item);
        }
    }

    PyMem_Free(m->items);
    m->items = items;
    m->capacity = new_capacity;
    return 0;
}

/*
 * Deallocate the map.
 *
 * This will call the deallocator passed to map_new() on
 * each of the stored values.
 */
void map_free(map* m) {
    for (Py_ssize_t i = 0; i < m->capacity; i++) {
        pair* item = m->items[i];
        if (item) {
            m->dealloc(item->value);
            PyMem_Free(item->key);
            PyMem_Free(item);
        }
    }

    PyMem_Free(m->items);
    PyMem_Free(m);
}


/*
 * Set a key and value on the map.
 *
 * If the map is at maximum capacity (e.g. 2 items set on a capacity of 2),
 * then, it is expanded by a factor of two.
 *
 * The key is hashed using an FNV hash function.
 */
void map_set(map* m, const char* key, void* value) {
    if (m->len >= m->capacity / 2)
        expand(m);
    set_entry(
        m->items,
        m->capacity,
        key,
        value,
        &m->len,
        m->dealloc
    );
}

// For debugging purposes
COLD void print_map(map* m, map_print_func pr) {
    puts("map {");
    for (int i = 0; i < m->capacity; i++) {
        pair* p = m->items[i];
        if (p) {
            printf(
                "\"%s\": ",
                p->key
            );
            pr(p->value);
            puts("");
        }
    }
    puts("}");
}
