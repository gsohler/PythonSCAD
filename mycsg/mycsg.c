#include <Python.h>
#include <stdio.h>

#include "mesh.h"
#include "bsp_mesh.h"


// All code is copied from github.com/sshirokov/csgtool




// 0=union, 1=difference, 2=intersection
mesh_t *bsp_operation(mesh_t *mesh1, mesh_t *mesh2,int mode)
{
        bsp_node_t *result = NULL;
        bsp_node_t *bsp1 = NULL;
        bsp_node_t *bsp2 = NULL;
        mesh_t *out = NULL;

	if(mesh1 == NULL) return;
	if(mesh2 == NULL) return;

	do
	{
	        bsp1 = mesh_to_bsp(mesh1);
	        bsp2 = mesh_to_bsp(mesh2);

		if(bsp1 == NULL) break;
		if(bsp2 == NULL) break;

	        // Operate
		switch(mode)
		{
			case 0:
			        result = bsp_union(bsp1, bsp2);
				break;
			case 1:
			        result = bsp_subtract(bsp1, bsp2);
				break;
			case 2:
			        result = bsp_intersect(bsp1, bsp2);
				break;
		}

	        if(bsp1 != NULL) free_bsp_tree(bsp1);
	        if(bsp2 != NULL) free_bsp_tree(bsp2);

		if(result == NULL) break;
        	out = NEW(bsp_mesh_t, "BSP", result);
		return out;
	} while(0);
        if(bsp1 != NULL) free_bsp_tree(bsp1);
        if(bsp2 != NULL) free_bsp_tree(bsp2);
        if(result != NULL) free_bsp_tree(result);
        return NULL;


}

static PyObject *mycsg_union(PyObject *self, PyObject *args)
{
  mesh_t *out;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *keys;
  if (!PyArg_ParseTuple(args, "OO",&arg1, &arg2)) {
    return NULL;
  }
  Py_INCREF(arg1);
  Py_INCREF(arg2);
  printf("%d %p\n",arg1->ob_refcnt,arg1->ob_type);
//  keys = PyDict_Keys(arg1);
//  printf("keys are %p\n",keys);

  printf("Union !\n");
//        mesh1 = mesh_read_file(path1);
//        check(mesh1 != NULL, "Failed to read mesh from '%s'", path1);
//        log_info("Loaded file: %s %d facets", path1, mesh1->poly_count(mesh1));
//        if(mesh1 != NULL) mesh1->destroy(mesh1);
//        if(mesh2 != NULL) mesh2->destroy(mesh2);
//        check(out->write(out, out_path, "STL") == 0, "Failed to write STL to %s", out_path);
//        out->destroy(out);
  out = bsp_operation(NULL, NULL, 0);
  Py_DECREF(arg1);
  Py_DECREF(arg2);
  Py_INCREF(Py_None);
  return Py_None;
}

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
  {"printHello", mycsg_printHello, METH_VARARGS , "Prints ’Hello World’."},
  {"union", mycsg_union, METH_VARARGS , "Builds the Union of two STLs."},
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

