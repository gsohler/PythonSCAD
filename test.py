
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




global CutPlaneStraight
def CutPlaneStraight(plpos,pldir,s,sd): # Flaeche mit Gerade  s, s-dir schneiden: punkt
        h =np.dot(pldir,sd) 
        if math.fabs(h) < 0.001:
                return None
        q=(np.dot(pldir,plpos)-np.dot(pldir,s))/h  
        return s + ( sd * q )

global CutPlanePlane
def CutPlanePlane(p1,n1, p2,n2): # return list(pos, dir)
	n3 = np.cross(n1,n2)
	n3s=np.linalg.norm(n3)
        if math.fabs(n3s) < 0.001:
                return None,None
	n3 = n3/n3s

        nx=np.cross(n1,n3)
        p3=CutPlaneStraight(p2,n2,p1,nx)
	if p3 is None:
		return None
        return p3,n3



global read_bpt
def read_bpt(file):
        lines = [line.rstrip('\n') for line in open(file)]
        count=int(lines.pop(0))
        for n in range(count):
                dim=lines.pop(0).strip().split()
                table=[]
                for j in range(int(dim[0])+1):
                        row=[]
                        for i in range(int(dim[0])+1):
                                line = lines.pop(0)
                                field=line.strip().split()
                                pts=[float(field[1]),float(field[0]),float(field[2])]
                                row.append(pts)
                        table.append(row)
		table=table[::-1]		
		bezier_surface(table,10,-2)
	concat(count)


global import_obj
def import_obj(filename):
	obj=pymesh.load_mesh(filename)
	meshstack.append(obj)
	pass

def compile():
#	cube([10,10,10])
#	translate([-5,-5,-5])
#	cylinder(r=3,h=10)
#	difference()
#	size(2)
	import_obj("gear.stl")
#	enterprise()
#	mirror([1,1,1])
#	angtest()
#	rotate_demo()

	pts=[[[0,0,0],[1,0,1]],[[0,1,1],[1,1,0]]]
#	bezier_surface(pts,10)
#	read_bpt("teapot.bpt")
#	cube([1,1,1])
	

compile()


