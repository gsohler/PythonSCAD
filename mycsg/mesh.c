#include "dbg.h"

#include "stl.h"
#include "export.h"
#include "mesh.h"
#include "reader.h"
#include "bsp.h"

int mesh_init(void *self, void *unused) {
	if(self == NULL) return -1;
	return 0;
}

char* mesh_describe(void *self) {
	mesh_t *mesh = (mesh_t*)self;
	return mesh->type;
}

void free_mesh(void *self) {
	if(self != NULL) free(self);
	return;
}

void destroy_mesh(void *self) {
	mesh_t *mesh = (mesh_t*)self;
	if(mesh->destroy != NULL) {
		mesh->destroy(mesh);
	}
	else {
		free_mesh(mesh);
	}
}

int _default_poly_count(void *self) {
	return 0;
}

klist_t(poly)* _default_to_polygons(void *self) {
	return NULL;
}

int _default_write(void *self, char *path, char type[4]) {
	int rc = -1;
	mesh_t *mesh = (mesh_t*)self;
	stl_object *stl = NULL;
	klist_t(poly) *polys = NULL;
	klist_t(poly) *triangles = NULL;

	// This is the only format we speak right now
	if(strncmp(type, "STL", 3) != 0) goto error;

	check((polys = mesh->to_polygons(mesh)) != NULL, "Failed to get polygons from mesh %p", mesh);

	triangles = polys_to_tris(NULL, polys);
	check(triangles != NULL, "Failed to convert polygons to trianges.");

	// The default output format is STL
	stl = stl_from_polys(triangles);
	check(stl != NULL, "Failed to generate STL object for write.");
	rc = stl_write_file(stl, path);

	if(stl != NULL) stl_free(stl);
	if(polys != NULL) kl_destroy(poly, polys);
	if(triangles != NULL) kl_destroy(poly, triangles);
	return rc;
error:
	if(stl != NULL) stl_free(stl);
	if(polys != NULL) kl_destroy(poly, polys);
	if(triangles != NULL) kl_destroy(poly, triangles);
	return -1;
}

bsp_node_t* _default_to_bsp(void *self) {
	mesh_t *mesh = (mesh_t*)self;
	bsp_node_t *bsp = NULL;
	klist_t(poly)* polys = NULL;

	check((polys = mesh->to_polygons(mesh)) != NULL,
		  "Failed to convert mesh %p to poly list", mesh);

	check((bsp = bsp_build(NULL, polys, 1)) != NULL,
		  "Failed to build BSP tree from %zd polygons of %p", polys->size, self);

	kl_destroy(poly, polys);
	return bsp;
error:
	if(polys != NULL) kl_destroy(poly, polys);
	if(bsp != NULL) free_bsp_tree(bsp);
	return NULL;
}

void *alloc_mesh(size_t size, mesh_t proto, char type[4], void *data) {
	if(proto.init == NULL) proto.init = mesh_init;
	if(proto.destroy == NULL) proto.destroy = free_mesh;
	if(proto.poly_count == NULL) proto.poly_count = _default_poly_count;
	if(proto.to_polygons == NULL) proto.to_polygons = _default_to_polygons;
	if(proto.write == NULL) proto.write = _default_write;
	if(proto.to_bsp == NULL) proto.to_bsp = _default_to_bsp;

	mesh_t *m = calloc(1, size);
	*m = proto;
	strncpy(m->type, type, 3);

	check(m->init(m, data) != -1, "Failed to initialize %p(%s, %p)", m, m->type, data);
	return m;
error:
	if(m != NULL) m->destroy(m);
	return NULL;
}

mesh_t *mesh_read_file(char *path) {
	return reader_load(path);
}
