#ifndef UNDEFINED_H
#define UNDEFINED_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

typedef struct {
    PyObject_HEAD
} UndefinedObject;

extern PyTypeObject UndefinedType;

// Eksportuj jako PyObject*, nie strukturę
extern PyObject *Undefined;

#endif // UNDEFINED_H