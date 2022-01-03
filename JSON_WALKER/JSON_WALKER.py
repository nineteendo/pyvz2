#JSON WALKER BY CLC2020
import os
c=d=0
try:
        os.remove("t.txt")
except:
        0
for b in open("ZOMBIETYPES.json",'r').readlines():
#depth x containes { x
#	if "{" in b:
#		c+=b.count("{")
#depth x containes } x-1
	if "}" in b:
		c-=b.count("}")
#depth x containes [ x
#	if "[" in b:
#		d+=b.count("[")
#depth x containes ] x-1
	if "]" in b:
		d-=b.count("]")
	open("t.txt",'a').write(str(c)+","+str(d)+b)
#depth x containes { x+1
	if "{" in b:
		c+=b.count("{")
#depth x containes } x
#	if "}" in b:
#		c-=b.count("}")
#depth x containes [ x+1
	if "[" in b:
		d+=b.count("[")
#depth x containes ] x
#	if "]" in b:
#		d-=b.count("]")
os.system("open t.txt")
