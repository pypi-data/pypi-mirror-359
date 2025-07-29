#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Tuple object structure
typedef struct {
    PyObject_HEAD
    PyObject *orig; // Original tuple object
} Tuple;

// External type declaration
extern PyTypeObject TupleType;