#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "Undefined.h"
#include "Object.h"

static PyObject *Undefined_repr(UndefinedObject *self) {
    (void) self;
    return PyUnicode_FromString("Undefined");
}

static PyObject *Undefined_call(UndefinedObject *self, PyObject *args, PyObject *kwargs) {
    (void) args;
    (void) kwargs;
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *Undefined_getattr(UndefinedObject *self, PyObject *name) {
    (void) name;
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *Undefined_getitem(UndefinedObject *self, PyObject *key) {
    (void) key;
    Py_INCREF(self);
    return (PyObject *)self;
}

static PyObject *Undefined_eq(UndefinedObject *self, PyObject *other, int op) {
    (void) self;
    int is_equal = (other == Py_None || PyObject_TypeCheck(other, &UndefinedType));

    if (op == Py_EQ) {
        if (is_equal)
            Py_RETURN_TRUE;
        else
            Py_RETURN_FALSE;
    } else if (op == Py_NE) {
        if (is_equal)
            Py_RETURN_FALSE;
        else
            Py_RETURN_TRUE;
    }

    Py_RETURN_NOTIMPLEMENTED;
}

static int Undefined_bool(UndefinedObject *self) {
    (void) self;
    return 0;
}

static Py_ssize_t Undefined_len(PyObject *Py_UNUSED(self)) {
    return 0;
}

static PyNumberMethods Undefined_as_number = {
    .nb_bool = (inquiry)Undefined_bool,
};

static PyMappingMethods Undefined_as_mapping = {
    .mp_length = (lenfunc)Undefined_len,
    .mp_subscript = (binaryfunc)Undefined_getitem,
};

static Py_hash_t Undefined_hash(UndefinedObject *self) {
    return (Py_hash_t)(uintptr_t)self;
}

PyTypeObject UndefinedType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "UndefinedType",
    .tp_basicsize = sizeof(UndefinedObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_doc = "Singleton representing JavaScript-like 'undefined'",
    .tp_repr = (reprfunc)Undefined_repr,
    .tp_call = (ternaryfunc)Undefined_call,
    .tp_getattro = (getattrofunc)Undefined_getattr,
    .tp_as_mapping = &Undefined_as_mapping,
    .tp_richcompare = (richcmpfunc)Undefined_eq,
    .tp_as_number = &Undefined_as_number,
    .tp_hash = (hashfunc)Undefined_hash,
};

static UndefinedObject _Undefined;
PyObject *Undefined = (PyObject *)&_Undefined;

// W PyInit_cjsify():
// PyObject_INIT(& _Undefined, &UndefinedType);
// Py_INCREF(Undefined);
