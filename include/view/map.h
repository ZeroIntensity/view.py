#ifndef VIEW_MAP_H
#define VIEW_MAP_H

#include <stdlib.h>

typedef struct STRUCT_MAP_PAIR {
    const char* key;
    void* value;
} pair;

typedef struct STRUCT_MAP {
    size_t len;
    size_t capacity;
    pair** items;
} map;

void* map_get(map* m, const char* key);
map* map_new(size_t inital_capacity);
void map_set(map* m, const char* key, void* value);
void map_free(map* m);
map* map_copy(map* m);

#endif
