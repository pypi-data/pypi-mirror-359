#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Tuple object structure
typedef struct {
    PyObject_HEAD
    PyObject *orig; // Original tuple object
} List;

// External type declaration
extern PyTypeObject ListType;
PyObject *List_dir(PyObject *self, PyObject *Py_UNUSED(args));
PyObject *List_getitem(PyObject *self, PyObject *key);