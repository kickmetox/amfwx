import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas,Color
from amfwx.shader import Shader,ShaderRenderer
from amfwx.render3d import identity
class S(Shader):
 def fragment(self,v): return Color(int(255*v[0]),int(255*v[1]),0)
c=Canvas(100,100); r=ShaderRenderer(100,100)
r.render(c,[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[(0,1,2),(0,2,3)],S(),identity(),uvs=[(0,0),(1,0),(1,1),(0,1)])
print(c.pixel(10,10), c.pixel(90,90))
