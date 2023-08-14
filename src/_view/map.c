#include <Python.h>
#include <stdint.h> // uint64_t
#include <stdio.h>
#include <stdlib.h> // size_t
#include <string.h> // strdup
#include <view/map.h>

#define FNV_OFFSET 14695981039346656037UL
#define FNV_PRIME 1099511628211UL

// https://en.wikipedia.org/wiki/Fowler–Noll–Vo_hash_function
static uint64_t hash_key(const char* key) {
    uint64_t hash = FNV_OFFSET;
    for (const char* p = key; *p; p++) {
        hash ^= (uint64_t)(unsigned char)(*p);
        hash *= FNV_PRIME;
    }
    return hash;
}

void* map_get(map* m, const char* key) {
    uint64_t hash = hash_key(key);
    size_t index = (size_t)(hash & (uint64_t)(m->capacity - 1));

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

map* map_new(size_t inital_capacity, map_free_func dealloc) {
    map* m = malloc(sizeof(map));
    if (!m)
        return (map*)PyErr_NoMemory();

    m->len = 0;
    m->capacity = inital_capacity;
    m->items = calloc(
        inital_capacity,
        sizeof(pair)
    );
    if (!m->items)
        return (map*)PyErr_NoMemory();
    m->dealloc = dealloc;
    return m;
}

static int set_entry(pair** items, size_t capacity, const char* key,
                     void* value, size_t* len, map_free_func dealloc) {
    uint64_t hash = hash_key(key);
    size_t index = (size_t)(hash & (uint64_t)(capacity - 1));

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
        items[index] = malloc(sizeof(pair));
        if (!items[index]) {
            PyErr_NoMemory();
            return -1;
        }
    }

    items[index]->key = key;
    items[index]->value = value;
    return 0;
}

static int expand(map* m) {
    size_t new_capacity = m->capacity * 2;
    if (new_capacity < m->capacity) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "integer limit reached on _view map capacity"
        );
        return -1;
    }
    pair** items = calloc(
        new_capacity,
        sizeof(pair)
    );
    if (!items) {
        PyErr_NoMemory();
        return -1;
    }

    for (int i = 0; i < m->capacity; i++) {
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
            free(item);
        }
    }

    free(m->items);
    m->items = items;
    m->capacity = new_capacity;
    return 0;
}

void map_free(map* m) {
    for (int i = 0; i < m->capacity; i++) {
        pair* item = m->items[i];
        if (item) {
            m->dealloc(item->value);
            free(item);
        }
    }

    free(m->items);
    free(m);
}

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

// Debugging purposes
void print_map(map* m, map_print_func pr) {
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
