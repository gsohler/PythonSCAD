global myobj

def myobj():
	cube([1,1,1])
	sphere(r=1);
	difference()
	return pop()

def matrix(obj):
	push(obj)
	translate([2,0,0])
	obj=myobj() # TODO weg
	push(obj)
	union()
	return pop()
	

obj=myobj()
dbl = matrix(obj)
show(dbl)

