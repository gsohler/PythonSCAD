
global ang_convert
def ang_convert():
	if len(meshstack) == 0:
        	message("No Object to convert")
		return

	obj=meshstack.pop()

	vertices = np.empty([len(obj.vertices),3],dtype=float)
	for i in range(len(obj.vertices)):
		ang=obj.vertices[i][0]
		r=obj.vertices[i][1]
		vertices[i][0]=-r*math.cos(ang)
		vertices[i][1]=r*math.sin(ang)
		vertices[i][2]=obj.vertices[i][2]
        meshstack.append(pymesh.form_mesh(vertices,obj.faces))


global hull
def hull():
	if len(meshstack) == 0:
        	message("No Object to hull")
		return

	obj=meshstack.pop()
	obj=pymesh.convex_hull(obj)
	meshstack.append(obj)


global collapse_short_edges
def collapse_short_edges(eps):
	if len(meshstack) == 0:
        	message("No Object to collapse")
		return

	obj=meshstack.pop()
	obj,info = pymesh.collapse_short_edges(obj,eps)
	meshstack.append(obj)

global split_long_edges
def split_long_edges(eps):
	if len(meshstack) == 0:
        	message("No Object to split")
		return

	obj=meshstack.pop()
	obj,info = pymesh.split_long_edges(obj,eps)
	meshstack.append(obj)



global antisnore
def antisnore():
	path=[[0,0],[20,0],[20,20],[10,20],[10,10],[0,10]]
	path=bezier(path,20)
	polygon(path)
	rotate_extrude(n=30)

#	square([2,10])
#	translate([22,3])
#	rotate_extrude(a1=-20,a2=20)
#	square([22,2])
#	translate([0,7])
#	rotate_extrude(a1=-20,a2=20)


global angtest
def angtest():
	cylinder(r=10,h=1)
	rotate([90,0,0])
	translate([10,12,0])
	scale([0.1,1,1])
	ang_convert()


def compile():
	antisnore()
compile()


