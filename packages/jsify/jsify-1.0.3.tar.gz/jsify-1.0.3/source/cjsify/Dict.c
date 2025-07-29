#define PY_SSIZE_T_CLEAN
#include <stddef.h>
#include <Python.h>

#include "cjsify.h"
#include "Object.h"
#include "Dict.h"
#include "List.h"
#include "Tuple.h"

// ============================
// === Basic object methods ===
// ============================

// Initialization
static int Dict_init(Dict *self, PyObject *args, PyObject *kwargs) {
    if (Object_init((Object *) self, args, kwargs) == 0) {
        if (kwargs) {
            if (PyDict_Update(self->orig, kwargs) < 0)
                return -1;
        }
        return 0;
    } else return -1;
}

// ============================
// === Basic operations =======
// ============================

// Dict_getattr - najpierw __dict__, potem Object_getattr
static PyObject *Dict_getattr(PyObject *self, PyObject *name) {
    if (PyUnicode_Check(name)) {
        if (PyUnicode_CompareWithASCIIString(name, "__dict__") == 0) {
            return unjsify(self);
        }
    }
    return Object_getattr(self, name);
}

// ============================
// === Type definition ========
// ============================

#ifdef _MSC_VER
    #ifndef __attribute__
        #define __attribute__(x)
    #endif
#endif

PySequenceMethods Dict_as_sequence = {};

PyTypeObject DictType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_base = &ObjectType,
    .tp_name = "Dict",
    .tp_basicsize = sizeof(Dict),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "JSON-like dictionary with attribute access",
    .tp_init = (initproc)Dict_init,

    .tp_as_mapping = &Object_as_mapping,

    .tp_getattro = (getattrofunc)Dict_getattr
};
