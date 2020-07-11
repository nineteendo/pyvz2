#DIFF TABLE FIRST-LAST VERSION by CLC2020
import os
added=[]
removed=[]
d=0
for dir in sorted(os.listdir()):
    if os.path.isdir(dir):
        current=[]
        added.append("#"+dir)
        a=""
        c=e=0
#change ZOMBIETYPES.json in a repeating path to search in folders/repeating path
        for b in open(os.path.join(dir,"ZOMBIETYPES.json"),'r').readlines():
#depth x containes { x
#            if "{" in b:
#                c+=b.count("{")
#depth x containes } x-1
            if "}" in b:
                c-=b.count("}")
#depth x containes [ x
#            if "[" in b:
#                e+=b.count("[")
#depth x containes ] x-1
            if "]" in b:
                e-=b.count("]")
            if c==2 and e==2:
                a+=b[17:-2
                     ]+"	"
                if a.count("	")>d:
                    d=a.count("	")
            elif a != "":
                current.append(a)
                if not a in added:
                    added.append(a)
                a=""
#depth x containes { x+1
            if "{" in b:
                c+=b.count("{")
#depth x containes } x
#            if "}" in b:
#                c-=b.count("}")
#depth x containes [ x+1
            if "[" in b:
                e+=b.count("[")
#depth x containes ] x
#            if "]" in b:
#                e-=b.count("]")
        for b in added:
            if not(b in current or b in removed):
                removed.append(b)
g=open("t.tsv","w")
for a in added:
    if "#" in a: 
        e+=1
        #g=open("t.tsv","a")
        if e==1:
            g.write(d*"	"+'found in')
    else:
        c=0
        g.write('''
'''+a+(d-a.count("	"))*"	")
        for b in removed:
            if a==b:
                g.write(f)
            if "#" in b:
                f=b[1:]
                c+=1
                if e==c:
                    g.write(f+"-")
g.close()
os.system("open -a Microsoft\ Excel t.tsv")
