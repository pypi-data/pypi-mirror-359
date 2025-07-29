#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *jsify(PyObject *obj);
PyObject *unjsify(PyObject *obj);

extern PyObject *deepcopy_func;
extern PyObject *copy_func;
