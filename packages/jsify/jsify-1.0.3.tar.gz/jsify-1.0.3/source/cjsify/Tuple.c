#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

#include "cjsify.h"
#include "Object.h"
#include "Tuple.h"
#include "Dict.h"
#include "List.h"

// ============================
// === Helper macros ==========
// ============================

#include "Macro.h"

// ============================
// === Main Tuple methods =====
// ============================

// count(value)
static PyObject *Tuple_count(PyObject *self, PyObject *args) {
    PyObject *value;
    if (!PyArg_ParseTuple(args, "O", &value))
        return NULL;

    return PyObject_CallMethod(((Tuple *)self)->orig, "count", "O", value);
}

// index(value)
static PyObject *Tuple_index(PyObject *self, PyObject *value) {
    Py_ssize_t idx = PySequence_Index(((Tuple *)self)->orig, value);
    if (idx == -1 && PyErr_Occurred())
        return NULL;
    return PyLong_FromSsize_t(idx);
}

// ============================
// === Method tables ==========
// ============================

static PyMethodDef Tuple_methods[] = {
    {"count", (PyCFunction)Tuple_count, METH_VARARGS, NULL},
    {"index", (PyCFunction)Tuple_index, METH_O, NULL},
    {"copy",(PyCFunction)Object_copy, METH_NOARGS, NULL},
    {"__dir__", (PyCFunction)List_dir, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static PyMappingMethods Tuple_as_mapping = {
    .mp_length = (lenfunc)Object_len,
    .mp_subscript = (binaryfunc)List_getitem,
};

// ============================
// === Type definition ========
// ============================

#ifdef _MSC_VER
    #ifndef __attribute__
        #define __attribute__(x)
    #endif
#endif

PyTypeObject TupleType __attribute__((used)) = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_base = &ObjectType,
    .tp_name = "Tuple",
    .tp_basicsize = sizeof(Tuple),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "JSON-like tuple object with attribute access",

    .tp_methods = Tuple_methods,
    .tp_as_mapping = &Tuple_as_mapping,
    .tp_as_sequence = &Object_as_sequence,
};
