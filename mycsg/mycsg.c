#include <Python.h>
#include <stdio.h>

#include "mesh.h"
#include "bsp_mesh.h"
#include "stl_mesh.h"


// All code is copied from github.com/sshirokov/csgtool





bsp_node_t *mesh_to_bsp(mesh_t *mesh);
void v3_cross(float3 *result, float3 v1, float3 v2, int normalize);

typedef struct {
        mesh_t proto;
	klist_t(poly) *polygons;
} poly_mesh_t;

void dump_polygons(klist_t(poly)* polygons)
{
	kliter_t(poly) *iter;

        iter = kl_begin(polygons);
        for(; iter != kl_end(polygons); iter = kl_next(iter))
	{
		printf("item %p\n",kl_val(iter));
        }
}

int count_polygons(klist_t(poly)* list)
{
	int len=0;
	kliter_t(poly) *iter;
        iter = kl_begin(list);
        for(; iter != kl_end(list); iter = kl_next(iter))
	{
		len++;
        }
	return len;
}

int poly_mesh_init(void *self, void *data) {
	bsp_node_t *bsp = (bsp_node_t *) data;;
	poly_mesh_t *mesh = (poly_mesh_t*)self;
	printf("init called with data %p\n",bsp);

	mesh->polygons = bsp_to_polygons(bsp, 1, NULL);
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

	printf("polygons called self=%p\n",self);
	// *kl_pushp(poly, dst) = copy;
	poly_mesh_t *mesh = (poly_mesh_t*)self;
	return mesh->polygons;
//	return bsp_to_polygons(mesh->bsp, 0, NULL);
//	return polygons;
}

mesh_t poly_mesh_t_Proto = {
        .init = poly_mesh_init,
        .destroy = poly_mesh_destroy,
        .poly_count = poly_mesh_poly_count,
        .to_polygons = poly_mesh_to_polygons,
};


// 0=union, 1=difference, 2=intersection
mesh_t *bsp_operation(mesh_t *mesh1, mesh_t *mesh2,int mode)
{
        bsp_node_t *result = NULL;
        bsp_node_t *bsp1 = NULL;
        bsp_node_t *bsp2 = NULL;
        mesh_t *out = NULL;

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
        	out = NEW(poly_mesh_t, "poly", result);
		printf("out is\n");
		dump_polygons(((poly_mesh_t *)out)->polygons);
		return out;
	} while(0);
        if(bsp1 != NULL) free_bsp_tree(bsp1);
        if(bsp2 != NULL) free_bsp_tree(bsp2);
        if(result != NULL) free_bsp_tree(result);
        return NULL;


}



int _default_write(void *self, char *path, char type[4]);
bsp_node_t* _default_to_bsp(void *self);


mesh_t *Python2Mesh(PyObject *obj)
{
	poly_mesh_t *result=NULL;
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

	klist_t(poly) *polygons_m=NULL;
        polygons_m = kl_init(poly);


	do
	{
		if(obj == NULL) break;
		polygons = PyObject_GenericGetAttr(obj,str_polygons);
		if(polygons == NULL) break;
		n_polygons=PyList_Size(polygons);


//		printf("polygons len  is %d\n",n_polygons);
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

			*kl_pushp(poly, polygons_m) = poly_m;
//			printf("push\n");

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
		result = (poly_mesh_t *) malloc(sizeof(poly_mesh_t));
		if(result == NULL) return NULL ;

		result->proto.init=poly_mesh_init; // TODO use alloc function here ?
		result->proto.destroy = poly_mesh_destroy;
		result->proto.poly_count = poly_mesh_poly_count;
		result->proto.to_polygons = poly_mesh_to_polygons;
		result->proto.write = _default_write;
		result->proto.to_bsp = _default_to_bsp;
		result->polygons=polygons_m;

		return (mesh_t *) result;


	} while(0);
	// TODO free stuff ?
	return (mesh_t *)result;
}

PyObject *Mesh2Python(mesh_t *mesh)
{
	int i,j;
	int n_polygons;
	PyObject *result=NULL;
	PyObject *str_polygons=PyUnicode_FromString("polygons"); // TODO free
	PyObject *str_vertices=PyUnicode_FromString("vertices");
	PyObject *str_pos=PyUnicode_FromString("pos");
	PyObject *str_x=PyUnicode_FromString("x");
	PyObject *str_y=PyUnicode_FromString("y");
	PyObject *str_z=PyUnicode_FromString("z");
	poly_mesh_t *poly_mesh = (poly_mesh_t *) mesh;
	poly_t *poly_m;

	PyObject *polygons,*polygon, *vertices, *vertex, *pos;
	kliter_t(poly) *poly_iter;
	
	n_polygons=count_polygons(poly_mesh->polygons);

	polygons = PyList_New(n_polygons);
        poly_iter = kl_begin(poly_mesh->polygons);
	i=0;
        for(; poly_iter != kl_end(poly_mesh->polygons); poly_iter = kl_next(poly_iter))
	{
		poly_m = kl_val(poly_iter); 
		vertices = PyList_New(poly_m->vertex_count);
		for(j=0;j<poly_m->vertex_count;j++)
		{
			pos = PyDict_New();

			PyDict_SetItem(pos,str_x, Py_BuildValue("f",poly_m->vertices[j][0]));
			PyDict_SetItem(pos,str_y, Py_BuildValue("f",poly_m->vertices[j][1]));
			PyDict_SetItem(pos,str_z, Py_BuildValue("f",poly_m->vertices[j][2]));

			vertex = PyDict_New();
			PyDict_SetItem(vertex,str_pos,pos);

			PyList_SetItem(vertices,j,vertex);
		}

		polygon = PyDict_New();
		PyDict_SetItem(polygon,str_vertices,vertices);

		// Calculate Normal
                float3 *fvs = poly_m->vertices;
                float3 v1 = {fvs[0][0] - fvs[1][0], fvs[0][1] - fvs[1][1], fvs[0][2] - fvs[1][2]};
       	        float3 v2 = {fvs[0][0] - fvs[2][0], fvs[0][1] - fvs[2][1], fvs[0][2] - fvs[2][2]};
               	v3_cross(&poly_m->normal, v1, v2, 1);

		PyList_SetItem(polygons,i,polygon);
		i++;
	}

	result = PyDict_New();
	PyDict_SetItem(result,str_polygons,polygons);
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

