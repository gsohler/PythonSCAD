#include "stl_mesh.h"
#include "util.h"

// Mesh type prototype methods
int stl_mesh_init(void *self, void *data) {
	stl_mesh_t *mesh = (stl_mesh_t*)self;
	if(data == NULL) {
		assert_mem(mesh->stl = stl_alloc(NULL, 0));
	}
	else {
		mesh->stl = (stl_object*)data;
	}
	return 0;
}

void stl_mesh_destroy(void *self) {
	stl_mesh_t *mesh = (stl_mesh_t*)self;
	stl_free(mesh->stl);
	free(self);
}

int stl_mesh_poly_count(void *self) {
	stl_mesh_t *mesh = (stl_mesh_t*)self;
	return mesh->stl->facet_count;
}

klist_t(poly)* stl_mesh_to_polygons_guarded(void *self, bool guard) {
	stl_mesh_t *mesh = (stl_mesh_t*)self;
	int count = mesh->_(poly_count)(mesh);
	klist_t(poly)* polys = kl_init(poly);

	for(int i = 0; i < count; i++) {
		poly_t *poly = poly_make_triangle_guarded(mesh->stl->facets[i].vertices[0],
												  mesh->stl->facets[i].vertices[1],
												  mesh->stl->facets[i].vertices[2],
												  guard);
		if(poly != NULL) {
			*kl_pushp(poly, polys) = poly;
		}
	}


	return polys;
}

klist_t(poly)* stl_mesh_to_polygons(void *self) {
	return stl_mesh_to_polygons_guarded(self, true);
}

klist_t(poly)* stl_mesh_to_polygons_unsafe(void *self) {
	return stl_mesh_to_polygons_guarded(self, false);
}

// Mesh type definitions
mesh_t stl_mesh_t_Proto = {
	.init = stl_mesh_init,
	.destroy = stl_mesh_destroy,
	.poly_count = stl_mesh_poly_count,
	.to_polygons = stl_mesh_to_polygons
};
