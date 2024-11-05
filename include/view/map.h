#ifndef VIEW_MAP_H
#define VIEW_MAP_H

#include <Python.h> // Py_ssize_t

typedef void (* ViewMap_FreeFunc)(void *);
typedef void (* ViewMap_PrintFunc)(void *);

typedef struct STRUCT_MAP_PAIR
{
    char *key;
    void *value;
} _ViewMap_Pair;

typedef struct STRUCT_MAP
{
    Py_ssize_t len;
    Py_ssize_t capacity;
    _ViewMap_Pair **items;
    ViewMap_FreeFunc dealloc;
} ViewMap;

void * ViewMap_Get(ViewMap *m, const char *key);
ViewMap * ViewMap_New(Py_ssize_t inital_capacity, ViewMap_FreeFunc dealloc);
void ViewMap_Set(ViewMap *m, const char *key, void *value);
void ViewMap_Free(ViewMap *m);
ViewMap * ViewMap_Copy(ViewMap *m);
void ViewMap_Print(ViewMap *m, ViewMap_PrintFunc pr);

#endif
