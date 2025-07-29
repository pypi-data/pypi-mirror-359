#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

#include "cjsify.h"
#include "Object.h"
#include "List.h"
#include "Dict.h"
#include "Tuple.h"
#include "Undefined.h"
#include "Iterator.h"

// ============================
// === Helper macros ==========
// ============================

#include "Macro.h"


// ============================
// === Redirections ===========
// ============================

// Redirected operations
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _repr, PyObject_Repr)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _str, PyObject_Str)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _int, PyNumber_Long)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _float, PyNumber_Float)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _index, PyNumber_Index)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _pos, PyNumber_Positive)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _neg, PyNumber_Negative)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _abs, PyNumber_Absolute)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _invert, PyNumber_Invert)
Py_ssize_t REDIRECT_TO_ORIG_METHOD(Object, _len, PyObject_Length)
static int REDIRECT_TO_ORIG_METHOD(Object, _bool, PyObject_IsTrue)

static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _add, PyNumber_Add)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _sub, PyNumber_Subtract)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _mul, PyNumber_Multiply)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _floordiv, PyNumber_FloorDivide)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _truediv, PyNumber_TrueDivide)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _mod, PyNumber_Remainder)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _or, PyNumber_Or)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _and, PyNumber_And)

static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _lshift, PyNumber_Lshift)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _rshift, PyNumber_Rshift)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _xor, PyNumber_Xor)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _divmod, PyNumber_Divmod)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _matmul, PyNumber_MatrixMultiply)

//static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _iter, PyObject_GetIter)
static PyObject *REDIRECT_TO_ORIG_METHOD(Object, _iternext, PyIter_Next)

static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _iadd, PyNumber_InPlaceAdd)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _isub, PyNumber_InPlaceSubtract)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _imul, PyNumber_InPlaceMultiply)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _imod, PyNumber_InPlaceRemainder)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _ilshift, PyNumber_InPlaceLshift)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _irshift, PyNumber_InPlaceRshift)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _iand, PyNumber_InPlaceAnd)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _ixor, PyNumber_InPlaceXor)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _ior, PyNumber_InPlaceOr)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _ifloordiv, PyNumber_InPlaceFloorDivide)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _itruediv, PyNumber_InPlaceTrueDivide)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _imatmul, PyNumber_InPlaceMatrixMultiply)

static REDIRECT_TO_ORIG_TERNARY(PyObject *, Object, _ipow, PyNumber_InPlacePower)
static REDIRECT_TO_ORIG_TERNARY(PyObject *, Object, _pow, PyNumber_Power)

static REDIRECT_TO_ORIG_METHOD_1_ARG(int ,Object, _sq_contains, PySequence_Contains)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _sq_concat, PySequence_Concat)
static Py_ssize_t REDIRECT_TO_ORIG_METHOD(Object, _sq_len, PySequence_Length)
static REDIRECT_TO_ORIG_BINARY(PyObject *, Object, _sq_iconcat, PySequence_InPlaceConcat)

// ============================
// === Basic object methods ===
// ============================

// Deallocation
static void Object_dealloc(Object *self) {
    Py_XDECREF(self->orig);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

// New instance
static PyObject *Object_new(PyTypeObject *type, PyObject *args, PyObject *kwargs) {
    (void)args;
    (void)kwargs;
    Object *self = (Object *)type->tp_alloc(type, 0);
    if (!self) return NULL;
    return (PyObject *)self;
}

// Initialization
int Object_init(Object *self, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *orig;
    if (!PyArg_ParseTuple(args, "O", &orig)) {
        PyErr_SetString(PyExc_TypeError, "Expected a single object argument");
        return -1;
    }
    self->orig = unjsify(orig);
    return 0;
}

// ============================
// === Basic operations =======
// ============================

PyObject *Object_getitem(PyObject *self, PyObject *key) {
    PyObject *item = PyObject_GetItem(((Object *)self)->orig, key);
    if (!item) {
        PyErr_Clear();
        Py_INCREF(Undefined);
        return Undefined;
    }
    PyObject *result = jsify(item);
    Py_DECREF(item);
    return result;
}

// __hash__
static Py_hash_t Object_hash(PyObject *self) {
    return PyObject_Hash(((Object *)self)->orig);
}

// __setitem__ / __delitem__
int Object_ass_subscript(PyObject *self, PyObject *key, PyObject *value) {
    if (value == NULL)
        return PyObject_DelItem(((Object *)self)->orig, key);
    else {
        PyObject *orig = unjsify(value);
        int result = PyObject_SetItem(((Object *)self)->orig, key, orig);
        Py_DECREF(orig);
        return result;
        }
}

// Helper: find PyMethodDef* for method name in type or bases
static PyMethodDef* find_methoddef_in_type(PyTypeObject *type, const char *name) {
    while (type) {
        PyMethodDef *methods = type->tp_methods;
        if (methods) {
            for (; methods->ml_name != NULL; methods++) {
                if (strcmp(methods->ml_name, name) == 0)
                    return methods;
            }
        }
        type = type->tp_base;
    }
    return NULL;
}

PyObject *Object_getattr(PyObject *self, PyObject *name) {
    if (PyUnicode_Check(name)) {
        const char *attr = PyUnicode_AsUTF8(name);
        if (attr && attr[0] == '_' && attr[1] == '_' &&
            attr[strlen(attr) - 2] == '_' && attr[strlen(attr) - 1] == '_') {

            if (strcmp(attr, "__class__") == 0) {
                return (PyObject *)Py_TYPE(self);
            }
            if (strcmp(attr, "__name__") == 0 ||
                strcmp(attr, "__module__") == 0 ||
                strcmp(attr, "__doc__") == 0) {
                return PyObject_GenericGetAttr((PyObject *)Py_TYPE(self), name);
            }

            // In Object_getattro:
            PyMethodDef *methdef = find_methoddef_in_type(Py_TYPE(self), attr);
            if (methdef) {
                return PyCFunction_NewEx(methdef, self, (PyObject *)Py_TYPE(self));
            }

            // Otherwise delegate to orig
            return PyObject_GetAttr(((Object *)self)->orig, name);
        }
    }
    PyErr_Clear();
    PyObject *item = PyObject_GetItem(self, name);
    if (item) return item;

    PyErr_Clear();
    return PyObject_GenericGetAttr(self, name);
}

// __setattr__
static int Object_setattr(PyObject *self, PyObject *name, PyObject *value) {
    return Object_ass_subscript(self, name, value);
}

// ============================
// === Utility operations =====
// ============================

static PyObject *Object_richcompare(PyObject *self, PyObject *other, int op) {
    return PyObject_RichCompare(((Object *)self)->orig, other, op);
}

// ============================
// === Python methods =========
// ============================

// __deepcopy__
static PyObject *Object_deepcopy(PyObject *self, PyObject *memo) {
    PyObject *result = jsify(PyObject_CallFunctionObjArgs(deepcopy_func, ((Object *)self)->orig, memo, NULL));
    RETURN_JSIFIED(result);
}

// __copy__
PyObject *Object_copy(PyObject *self, PyObject *Py_UNUSED(ignored)) {
    PyObject *result = PyObject_CallFunctionObjArgs(copy_func, ((Object *)self)->orig, NULL);
    RETURN_JSIFIED(result);
}

// __sizeof__
static PyObject *Object_sizeof(PyObject *self, PyObject *Py_UNUSED(args)) {
    Py_ssize_t size = PyObject_Size(((Object *)self)->orig);
    return PyLong_FromSsize_t(size);
}

// __getstate__
PyObject *Object_getstate(PyObject *self, PyObject *Py_UNUSED(args)) {
    return unjsify(self);
}

// __setstate__
PyObject *Object_setstate(PyObject *self, PyObject *args) {
    PyObject *state;
    if (!PyArg_ParseTuple(args, "O", &state))
        return NULL;
    Py_XDECREF(((Object *)self)->orig);
    ((Object *)self)->orig = unjsify(state);
    Py_RETURN_NONE;
}

// __format__
static PyObject *Object_format(PyObject *self, PyObject *args) {
    PyObject *format_spec;
    if (!PyArg_ParseTuple(args, "O", &format_spec))
        return NULL;
    return PyObject_Format(((Object *)self)->orig, format_spec);
}

// __dir__
static PyObject *Object_dir(PyObject *self, PyObject *Py_UNUSED(args)) {
    PyObject *dir = ((Object *)self)->orig;
    Py_INCREF(dir);
    return dir;
}

// ============================
// === Sequence methods =======
// ============================

static PyObject *Object_sq_repeat(PyObject *self, Py_ssize_t count) {
    PyObject *result = PySequence_Repeat(((Object *)self)->orig, count);
    RETURN_JSIFIED(result);
}

static PyObject *Object_sq_getitem(PyObject *self, Py_ssize_t index) {
    PyObject *result = PySequence_GetItem(((Object *)self)->orig, index);
    RETURN_JSIFIED(result);
}

static int Object_ass_item(PyObject *self, Py_ssize_t index, PyObject *value) {
    PyObject *orig = unjsify(value);
    int result = PySequence_SetItem(((Object *)self)->orig, index, orig);
    Py_DECREF(orig);
    return result;
}

static PyObject *Object_sq_irepeat(PyObject *self, Py_ssize_t count) {
    return PySequence_InPlaceRepeat(((Object *)self)->orig, count);
}

// ============================
// === Iteration ==========
// ============================

static PyObject *Object_iter(PyObject *self) {
    PyObject *orig_iter = PyObject_GetIter(((Object *)self)->orig);
    if (!orig_iter)
        return NULL;

    // Wywołanie konstruktora typu Iterator z oryginalnym iteratorem jako argumentem
    PyObject *iter_obj = PyObject_CallFunctionObjArgs((PyObject *)&IteratorType, orig_iter, NULL);
    Py_DECREF(orig_iter);  // zmniejszamy refcount, bo PyObject_CallFunctionObjArgs inkrementuje

    return iter_obj;
}

// ============================
// === Method tables ==========
// ============================

static PyMethodDef Object_methods[] = {
    {"__deepcopy__", (PyCFunction)Object_deepcopy, METH_O, NULL},
    {"__copy__", (PyCFunction)Object_copy, METH_NOARGS, NULL},
    {"__getstate__", (PyCFunction)Object_getstate, METH_NOARGS, NULL},
    {"__setstate__", (PyCFunction)Object_setstate, METH_VARARGS, NULL},
    {"__format__", (PyCFunction)Object_format, METH_VARARGS, NULL},
    {"__sizeof__", (PyCFunction)Object_sizeof, METH_NOARGS, NULL},
    {"__dir__", (PyCFunction)Object_dir, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

PyMappingMethods Object_as_mapping = {
    .mp_length = (lenfunc)Object_len,
    .mp_subscript = (binaryfunc)Object_getitem,
    .mp_ass_subscript = (objobjargproc)Object_ass_subscript,
};

PySequenceMethods Object_as_sequence = {
    .sq_contains = (objobjproc)Object_sq_contains,
    .sq_length = (lenfunc)Object_sq_len,
    .sq_concat = (binaryfunc)Object_sq_concat,
    .sq_repeat = (ssizeargfunc)Object_sq_repeat,
    .sq_item = (ssizeargfunc)Object_sq_getitem,
    .was_sq_slice = 0,  // deprecated
    .sq_ass_item = (ssizeobjargproc)Object_ass_item,
    .was_sq_ass_slice = 0,  // deprecated
    .sq_inplace_concat = (binaryfunc)Object_sq_iconcat,
    .sq_inplace_repeat = (ssizeargfunc)Object_sq_irepeat,
};

PyNumberMethods Object_as_number = {
    .nb_int = (unaryfunc)Object_int,
    .nb_float = (unaryfunc)Object_float,
    .nb_index = (unaryfunc)Object_index,
    .nb_negative = (unaryfunc)Object_neg,
    .nb_positive = (unaryfunc)Object_pos,
    .nb_absolute = (unaryfunc)Object_abs,
    .nb_invert = (unaryfunc)Object_invert,

    .nb_add = (binaryfunc)Object_add,
    .nb_subtract = (binaryfunc)Object_sub,
    .nb_multiply = (binaryfunc)Object_mul,
    .nb_floor_divide = (binaryfunc)Object_floordiv,
    .nb_true_divide = (binaryfunc)Object_truediv,
    .nb_remainder = (binaryfunc)Object_mod,
    .nb_power = (ternaryfunc)Object_pow,
    .nb_or = (binaryfunc)Object_or,
    .nb_and = (binaryfunc)Object_and,

    .nb_divmod = (binaryfunc)Object_divmod,
    .nb_lshift = (binaryfunc)Object_lshift,
    .nb_rshift = (binaryfunc)Object_rshift,
    .nb_xor = (binaryfunc)Object_xor,
    .nb_matrix_multiply = (binaryfunc)Object_matmul,
    .nb_bool = (inquiry)Object_bool,

    .nb_inplace_add = (binaryfunc)Object_iadd,
    .nb_inplace_subtract = (binaryfunc)Object_isub,
    .nb_inplace_multiply = (binaryfunc)Object_imul,
    .nb_inplace_remainder = (binaryfunc)Object_imod,
    .nb_inplace_power = (ternaryfunc)Object_ipow,
    .nb_inplace_lshift = (binaryfunc)Object_ilshift,
    .nb_inplace_rshift = (binaryfunc)Object_irshift,
    .nb_inplace_and = (binaryfunc)Object_iand,
    .nb_inplace_xor = (binaryfunc)Object_ixor,
    .nb_inplace_or = (binaryfunc)Object_ior,
    .nb_inplace_floor_divide = (binaryfunc)Object_ifloordiv,
    .nb_inplace_true_divide = (binaryfunc)Object_itruediv,
    .nb_inplace_matrix_multiply = (binaryfunc)Object_imatmul,
};

// ============================
// === Type definition ========
// ============================

#ifdef _MSC_VER
    #ifndef __attribute__
        #define __attribute__(x)
    #endif
#endif

PyTypeObject ObjectType __attribute__((used)) = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "Object",
    .tp_basicsize = sizeof(Object),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_doc = "JSON-like object with attribute access",
    .tp_new = Object_new,
    .tp_init = (initproc)Object_init,
    .tp_dealloc = (destructor)Object_dealloc,

    .tp_repr = (reprfunc)Object_repr,
    .tp_str = (reprfunc)Object_str,
    .tp_hash = (hashfunc)Object_hash,

    .tp_methods = Object_methods,
    .tp_as_mapping = &Object_as_mapping,
    .tp_as_number = &Object_as_number,

    .tp_getattro = (getattrofunc)Object_getattr,
    .tp_setattro = (setattrofunc)Object_setattr,

    .tp_iter = (getiterfunc)Object_iter,
    .tp_iternext = (iternextfunc)Object_iternext,
    .tp_richcompare = (richcmpfunc)Object_richcompare,

};
