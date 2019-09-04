#include <Python.h>
#include <stdio.h>

#include "mesh.h"
#include "bsp_mesh.h"
#include "stl_mesh.h"


// All code is copied from github.com/sshirokov/csgtool




bsp_node_t *mesh_to_bsp(mesh_t *mesh);
void v3_cross(float3 *result, float3 v1, float3 v2, int normalize);

// 0=union, 1=difference, 2=intersection
mesh_t *bsp_operation(mesh_t *mesh1, mesh_t *mesh2,int mode)
{
        bsp_node_t *result = NULL;
        bsp_node_t *bsp1 = NULL;
        bsp_node_t *bsp2 = NULL;
        mesh_t *out = NULL;

	printf("bsp_operation\n");

	if(mesh1 == NULL) return NULL;
	if(mesh2 == NULL) return NULL;

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

int poly_mesh_init(void *self, void *data) {
	printf("init called\n");
//	bsp_mesh_t *mesh = (bsp_mesh_t*)self;
//	if(data == NULL) {
//		mesh->bsp = alloc_bsp_node();
//	}
//	else {
//		mesh->bsp = (bsp_node_t*)data;
//	}
	return 0;
}

void poly_mesh_destroy(void *self) {
	printf("destroy called\n");
//	bsp_mesh_t *mesh = (bsp_mesh_t*)self;
//	free_bsp_tree(mesh->bsp);
//	free(self);
}

int poly_mesh_poly_count(void *self) {
	printf("count called\n");
//	bsp_mesh_t *mesh = (bsp_mesh_t*)self;
//	return bsp_count_polygons(mesh->bsp);
	return 0;
}

klist_t(poly)* poly_mesh_to_polygons(void *self) {
	klist_t(poly) *polygons=NULL;
	printf("polygons called self=%p\n",self);
        polygons = kl_init(poly);
	// *kl_pushp(poly, dst) = copy;
//	bsp_mesh_t *mesh = (bsp_mesh_t*)self;
//	return bsp_to_polygons(mesh->bsp, 0, NULL);
	return polygons;
}


int _default_write(void *self, char *path, char type[4]);
bsp_node_t* _default_to_bsp(void *self);


mesh_t *Python2Mesh(PyObject *obj)
{
	mesh_t *result=NULL;
	int i,j,n_polygons,n_vertices;
	PyObject *str_polygons=PyUnicode_FromString("polygons"); // TODO free
	PyObject *str_vertices=PyUnicode_FromString("vertices");
	PyObject *str_pos=PyUnicode_FromString("pos");
	PyObject *str_x=PyUnicode_FromString("x");
	PyObject *str_y=PyUnicode_FromString("y");
	PyObject *str_z=PyUnicode_FromString("z");
	Py_INCREF(obj);
	PyObject *polygons, *polygon;
	PyObject *vertices, *vertex;
	PyObject *pos, *value;
	poly_t *poly_m;

//	stl_object *stl =  stl_alloc(NULL, 0);
//	strncpy(stl->header, sizeof(stl->header), "pythonscad");




	do
	{
		if(obj == NULL) break;
		polygons = PyObject_GenericGetAttr(obj,str_polygons);
		if(polygons == NULL) break;
		n_polygons=PyList_Size(polygons);

//		stl->facet_count = n_polygons;
//                stl->facets = calloc(n_polygons, sizeof(stl_facet));

		printf("polygons len  is %d\n",n_polygons);
		for(i=0;i<n_polygons;i++)
		{
			polygon =PyList_GetItem(polygons,i);
			if(polygon == NULL) continue;
			Py_INCREF(polygon);
			vertices = PyObject_GenericGetAttr(polygon,str_vertices);
			if(vertices == NULL) continue;
			n_vertices=PyList_Size(vertices);
			poly_m = malloc(sizeof(poly_t));
			if(poly_m == NULL) return NULL;
			poly_m->vertex_count=n_vertices;
			poly_m->vertex_max=n_vertices;
		       	poly_m->vertices = malloc(n_vertices * sizeof(float3));
			if(poly_m->vertices == NULL) continue; // TODO fix

			for(j=0;j<n_vertices;j++)
			{
				vertex =PyList_GetItem(vertices,j);
				if(vertex == NULL) continue;
				Py_INCREF(vertex);
				pos = PyObject_GenericGetAttr(vertex,str_pos);
				if(pos != NULL)
				{
					Py_INCREF(pos);
					value = PyObject_GenericGetAttr(pos,str_x);
					if(value != NULL)
						poly_m->vertices[j][0]  = PyFloat_AsDouble(value);
					value = PyObject_GenericGetAttr(pos,str_y);
					if(value != NULL)
						poly_m->vertices[j][1]  = PyFloat_AsDouble(value);
					value = PyObject_GenericGetAttr(pos,str_z);
					if(value != NULL)
						poly_m->vertices[j][2]  = PyFloat_AsDouble(value);
//					printf("%f/%f/%f\n",poly_m->vertices[j][0],poly_m->vertices[j][1],poly_m->vertices[j][2]);
					Py_DECREF(pos);
				}
				Py_DECREF(vertex);
			}
	                float3 *fvs = poly_m->vertices;
	                float3 v1 = {fvs[0][0] - fvs[1][0], fvs[0][1] - fvs[1][1], fvs[0][2] - fvs[1][2]};
        	        float3 v2 = {fvs[0][0] - fvs[2][0], fvs[0][1] - fvs[2][1], fvs[0][2] - fvs[2][2]};
                	v3_cross(&poly_m->normal, v1, v2, 1);
//			printf("%f %f %f\n",poly_m->normal[0],poly_m->normal[1],poly_m->normal[2]);

			// TODO hier poly_m in facets reinmachen, passt aber nicht

			Py_DECREF(polygon);
		}

// PyObject_GetAttr			

//        mesh1 = mesh_read_file(path1);
//        check(mesh1 != NULL, "Failed to read mesh from '%s'", path1);
//        log_info("Loaded file: %s %d facets", path1, mesh1->poly_count(mesh1));
//        if(mesh1 != NULL) mesh1->destroy(mesh1);
//        if(mesh2 != NULL) mesh2->destroy(mesh2);
//        check(out->write(out, out_path, "STL") == 0, "Failed to write STL to %s", out_path);
		Py_DECREF(obj);

		// finally create mesh_t here
		result = (mesh_t *) malloc(sizeof(mesh_t));
		if(result == NULL) return NULL ;

		result->init=poly_mesh_init;
		result->destroy = poly_mesh_destroy;
		result->poly_count = poly_mesh_poly_count;
		result->to_polygons = poly_mesh_to_polygons;
		result->write = _default_write;
		result->to_bsp = _default_to_bsp;

		return result;


	} while(0);
	return result;
}

PyObject *Mesh2Python(mesh_t *mesh)
{
	PyObject *result=NULL;
	result = Py_BuildValue("i",123);
        //out->destroy(mesh);
  	// Py_BuildValue(
	Py_INCREF(result);
	return result;
}
static PyObject *mycsg_union(PyObject *self, PyObject *args)
{
  PyObject *arg1;
  PyObject *arg2;
  PyObject *result;
  mesh_t *mesh1;
  mesh_t *mesh2;
  mesh_t *out;

  printf("Union !\n");

  if (!PyArg_ParseTuple(args, "OO",&arg1, &arg2)) {
    return NULL;
  }

  mesh1 = Python2Mesh(arg1);
  mesh2 = Python2Mesh(arg2);

  out = bsp_operation(mesh1, mesh2, 0);

  result = Mesh2Python(out);
  printf("result=%p\n",result);
  Py_INCREF(result);

  return result;
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

