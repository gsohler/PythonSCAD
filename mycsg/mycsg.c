#include <Python.h>
#include <stdio.h>

static PyObject *mycsg_printHello(PyObject *self, PyObject *args)
{
  if (!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  printf("Hello world!\n");
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef mycsgMethods[] = {
  {"printHello", mycsg_printHello, METH_VARARGS | METH_VARARGS,
    "Prints ’Hello World’."},
  {NULL, NULL, 0, NULL},
};

static struct PyModuleDef mycsgmodule = {
		PyModuleDef_HEAD_INIT,
		"mycsg",
		NULL,
		-1,
		mycsgMethods
};

PyMODINIT_FUNC
PyInit_mycsg(void)
{
	return PyModule_Create(&mycsgmodule);
}
