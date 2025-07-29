#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "Macro.h"
#include "cjsify.h"
#include "Iterator.h"

// ============================
// === Basic methods ==========
// ============================

// Deallocation
static void Iterator_dealloc(Iterator *self) {
    Py_XDECREF(self->iterator);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

// New
static PyObject *Iterator_new(PyTypeObject *type, PyObject *Py_UNUSED(args), PyObject *kwargs) {
    (void)kwargs;
    Iterator *self = (Iterator *)type->tp_alloc(type, 0);
    if (!self)
        return NULL;
    return (PyObject *)self;
}

// Init
static int Iterator_init(Iterator *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *obj;
    if (!PyArg_ParseTuple(args, "O", &obj))
        return -1;

    PyObject *unjsified = unjsify(obj);
    if (!unjsified)
        return -1;

    self->iterator = PyObject_GetIter(unjsified);
    Py_DECREF(unjsified);
    if (!self->iterator)
        return -1;

    return 0;
}

static PyObject *Iterator_iter(PyObject *self) {
    Py_INCREF(self);
    return self;
}

static PyObject *Iterator_iternext(PyObject *self) {
    PyObject *next = PyIter_Next(((Iterator *)self)->iterator);
    RETURN_JSIFIED(next);
}

// ============================
// === Type definition ========
// ============================

#ifdef _MSC_VER
    #ifndef __attribute__
        #define __attribute__(x)
    #endif
#endif

PyTypeObject IteratorType __attribute__((used)) = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "Iterator",
    .tp_basicsize = sizeof(Iterator),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "Iterator with jsify wrapping",
    .tp_new = Iterator_new,
    .tp_init = (initproc)Iterator_init,
    .tp_dealloc = (destructor)Iterator_dealloc,
    .tp_iter = Iterator_iter,
    .tp_iternext = Iterator_iternext,
};
