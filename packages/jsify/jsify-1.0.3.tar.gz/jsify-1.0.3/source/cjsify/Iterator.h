#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Iterator object structure
typedef struct {
    PyObject_HEAD
    PyObject *iterator; // Original iterator object
} Iterator;

// External type declaration
extern PyTypeObject IteratorType;
