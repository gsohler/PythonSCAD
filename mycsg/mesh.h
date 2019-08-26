#include <stdlib.h>

#include "poly.h"
#include "bsp.h"

#ifndef __MESH_H
#define __MESH_H

typedef struct s_mesh_t {
	char type[4];

	int (*init)(void *self, void *data);
	void (*destroy)(void *self);

	int (*poly_count)(void *self);
	klist_t(poly)* (*to_polygons)(void *self);
	bsp_node_t* (*to_bsp)(void *self);

	int (*write)(void *self, char *path, char type[4]);
} mesh_t;

int mesh_init(void *self, void *data);
void free_mesh(void *self);
void destroy_mesh(void *self);

void *alloc_mesh(size_t size, mesh_t proto, char type[4], void *data);

#define NEW(T, N, D) alloc_mesh(sizeof(T), T##_Proto, N, D)
#define _(M) proto.M

// Load wrapper to read better
mesh_t *mesh_read_file(char *path);

#endif
