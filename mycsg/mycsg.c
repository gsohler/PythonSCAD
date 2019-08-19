#include <Python.h>
#include <stdio.h>

static PyObject *hello_printHello(PyObject *self, PyObject *args)
{
  if (!PyArg_ParseTuple(args, "")) {
    return NULL;
  }
  printf("Hello world!\n");
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef helloMethods[] = {
  {"printHello", hello_printHello, METH_VARARGS,
    "Prints ’Hello World’."},
  {NULL, NULL, 0, NULL},
};

void inithello(void)
{
  Py_InitModule("hello", helloMethods);
}