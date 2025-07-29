#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "cjsify.h"
#include "Object.h"
#include "List.h"
#include "Undefined.h"

// ============================
// === Helper macros ==========
// ============================

#include "Macro.h"

// ============================
// === Redirections ===========
// ============================

static PyObject *REDIRECT_TO_ORIG_METHOD_CALL(List, _clear, "clear")
static PyObject *REDIRECT_TO_ORIG_METHOD_CALL(List, _reverse, "reverse")
static REDIRECT_TO_ORIG_METHOD_CALL_O_ARGS(PyObject *, List, _count, "count")
static REDIRECT_TO_ORIG_METHOD_CALL_O_ARGS(PyObject *, List, _extend, "extend")
static REDIRECT_TO_ORIG_METHOD_CALL_O_ARGS(PyObject *, List, _index, "index")
static REDIRECT_TO_ORIG_METHOD_CALL_O_ARGS(PyObject *, List, _remove, "remove")

// ============================
// === Basic operations =======
// ============================

// __getitem__
PyObject *List_getitem(PyObject *self, PyObject *key) {
    if (PyLong_Check(key)) {
        Py_ssize_t idx = PyLong_AsSsize_t(key);
        PyObject *orig = ((List *)self)->orig;
        Py_ssize_t size = PySequence_Size(orig);
        if (idx < 0)
            idx += size;
        if (idx < 0 || idx >= size) {
            Py_INCREF(Undefined);
            return Undefined;
        }
        PyObject *value = PySequence_GetItem(orig, idx);
        RETURN_JSIFIED(value);
    }

    if (PySlice_Check(key)) {
        PyObject *value = PyObject_GetItem(((List *)self)->orig, key);
        RETURN_JSIFIED(value);
    }

    if (PyUnicode_Check(key)) {
        const char *str = PyUnicode_AsUTF8(key);
        char *endptr;
        long index = strtol(str, &endptr, 10);
        if (*endptr == '\0') {
            Py_ssize_t list_size = PyList_Size(((List *)self)->orig);
            if (index < 0)
                index += list_size;
            if (index < 0 || index >= list_size) {
                Py_INCREF(Undefined);
                return Undefined;
            }
            PyObject *value = PyList_GetItem(((List *)self)->orig, index);
            return jsify(value);
        }
    }

    // fallback to attribute lookup
    PyObject *value = PyObject_GenericGetAttr(((List *)self)->orig, key);
    RETURN_JSIFIED(value);
}


// __setitem__ / __delitem__
static int List_ass_subscript(PyObject *self, PyObject *key, PyObject *value) {
    if (!PyLong_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "List indices must be integers");
        return -1;
    }
    Py_ssize_t index = PyLong_AsSsize_t(key);
    if (value == NULL)
        return PySequence_DelItem(((List *)self)->orig, index);
    else
        {
            PyObject *orig = unjsify(value);
            int result = PySequence_SetItem(((List *)self)->orig, index, orig);
            Py_DECREF(orig);
            return result;
        }
}

// ============================
// === List-specific methods ==
// ============================

// append
static PyObject *List_append(PyObject *self, PyObject *obj) {
    PyObject *orig = unjsify(obj);
    int res = PyList_Append(((List *)self)->orig, orig);
    Py_DECREF(orig);
    if (res == 0) {
        Py_RETURN_NONE;
    } else {
        return NULL;
    }
}

static PyObject *List_insert(PyObject *self, PyObject *args) {
    Py_ssize_t index;
    PyObject *obj;
    if (!PyArg_ParseTuple(args, "nO", &index, &obj))
        return NULL;
    PyObject *orig = unjsify(obj);
    int res = PyList_Insert(((List *)self)->orig, index, orig);
    Py_DECREF(orig);
    if (res == 0) {
        Py_RETURN_NONE;
    } else {
        return NULL;
    }
}

// pop
static PyObject *List_pop(PyObject *self, PyObject *args) {
    Py_ssize_t index = -1;
    if (!PyArg_ParseTuple(args, "|n", &index))
        return NULL;
    if (index == -1)
        return PyObject_CallMethod(((List *)self)->orig, "pop", NULL);
    else
        return PyObject_CallMethod(((List *)self)->orig, "pop", "n", index);
}

// sort
static PyObject *List_sort(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *surt_func = PyObject_GetAttrString(((List *)self)->orig, "sort");
    if (!surt_func)
        return NULL;
    PyObject *result = PyObject_Call(surt_func, args, kwargs);
    Py_DECREF(surt_func);
    return result;
}

PyObject *List_dir(PyObject *self, PyObject *Py_UNUSED(args)) {
    Py_ssize_t len = PyObject_Size(((Object *)self)->orig);
    if (len < 0)
        return NULL;

    PyObject *dir = PyTuple_New(len);
    if (!dir)
        return NULL;

    for (Py_ssize_t i = 0; i < len; ++i) {
        char buf[32];
        snprintf(buf, sizeof(buf), "%zd", i);
        PyObject *str = PyUnicode_FromString(buf);
        if (!str) {
            Py_DECREF(dir);
            return NULL;
        }
        PyTuple_SET_ITEM(dir, i, str);  // no INCREF needed
    }

    return dir;
}

// ============================
// === Method tables ==========
// ============================

static PyMethodDef List_methods[] = {
    {"append", (PyCFunction)List_append, METH_O, NULL},
    {"clear", (PyCFunction)List_clear, METH_NOARGS, NULL},
    {"count", (PyCFunction)List_count, METH_O, NULL},
    {"extend", (PyCFunction)List_extend, METH_O, NULL},
    {"index", (PyCFunction)List_index, METH_O, NULL},
    {"insert", (PyCFunction)List_insert, METH_VARARGS, NULL},
    {"pop", (PyCFunction)List_pop, METH_VARARGS, NULL},
    {"remove", (PyCFunction)List_remove, METH_O, NULL},
    {"reverse", (PyCFunction)List_reverse, METH_NOARGS, NULL},
    {"sort", (PyCFunction)(void(*)(void))List_sort, METH_VARARGS | METH_KEYWORDS, NULL},
    {"copy",(PyCFunction)Object_copy, METH_NOARGS, NULL},
    {"__dir__", (PyCFunction)List_dir, METH_NOARGS, NULL},
    {"__getstate__", (PyCFunction)Object_getstate, METH_NOARGS, NULL},
    {"__setstate__", (PyCFunction)Object_setstate, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

// ============================
// === Type definition ========
// ============================

#ifdef _MSC_VER
    #ifndef __attribute__
        #define __attribute__(x)
    #endif
#endif

static PyMappingMethods List_as_mapping = {
    .mp_length = (lenfunc)Object_len,
    .mp_subscript = (binaryfunc)List_getitem,
    .mp_ass_subscript = (objobjargproc)List_ass_subscript,
};

PyTypeObject ListType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_base = &ObjectType,
    .tp_name = "List",
    .tp_basicsize = sizeof(List),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "JSON-like list with attribute access",

    .tp_methods = List_methods,
    .tp_as_sequence = &Object_as_sequence,
    .tp_as_mapping = &List_as_mapping

};
