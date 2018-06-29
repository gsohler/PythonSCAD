
global rotate_profile
def rotate_profile(i):
	square(10)
	translate([-5,-5])
	rotate(1.5*i)
	translate([15,0])
	

global rotate_demo
def rotate_demo():
	rotate_extrude(func=rotate_profile,n=180)

global enterprise
def enterprise():
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
	cylinder(r=15,h=1)
	rotate([92.5,0,2.5])
	translate([10,0,0])
	translate([[0,20,40,60,80,100,120,140],20,0])
	

	dup()
	translate([10,0,20])
	union()


	scale([6.283/160.0,1,1])
	ang_convert(7,15)


def compile():
	enterprise()
	mirror([1,1,1])
#	angtest()
#	rotate_demo()

compile()


