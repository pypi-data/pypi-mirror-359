#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Definition of Object structure
typedef struct {
    PyObject_HEAD
    PyObject *orig; // Wrapped original object
} Object;

extern PyTypeObject ObjectType;
extern PyMappingMethods Object_as_mapping ;
extern PySequenceMethods Object_as_sequence;
extern PyNumberMethods Object_as_number;

// Forward declarations from Object
int Object_init(Object *self, PyObject *args, PyObject *kwargs);
PyObject *Object_getattr(PyObject *self, PyObject *name);
PyObject *Object_getitem(PyObject *self, PyObject *key);
int Object_ass_subscript(PyObject *self, PyObject *key, PyObject *value);
Py_ssize_t Object_len(PyObject *self);
PyObject *Object_getstate(PyObject *self, PyObject *Py_UNUSED(args));
PyObject *Object_setstate(PyObject *self, PyObject *args);
PyObject *Object_copy(PyObject *self, PyObject *Py_UNUSED(ignored));