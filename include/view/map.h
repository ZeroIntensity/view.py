#ifndef VIEW_MAP_H
#define VIEW_MAP_H

#include <Python.h> // Py_ssize_t

typedef void (* map_free_func)(void *);
typedef void (* map_print_func)(void *);

typedef struct STRUCT_MAP_PAIR
{
    char *key;
    void *value;
} pair;

typedef struct STRUCT_MAP
{
    Py_ssize_t len;
    Py_ssize_t capacity;
    pair **items;
    map_free_func dealloc;
} map;

void * map_get(map *m, const char *key);
map * map_new(Py_ssize_t inital_capacity, map_free_func dealloc);
void map_set(map *m, const char *key, void *value);
void map_free(map *m);
map * map_copy(map *m);
void print_map(map *m, map_print_func pr);

#endif
