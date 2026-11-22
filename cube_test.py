import sys, math
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas, Color
from amfwx.render3d import *
c=Canvas(240,200,Color(10,12,18)); r=SoftwareRenderer(240,200)
model=multiply(translate(0,0,-3), rotate_y(0.6))
view=look_at((0,0,2),(0,0,0)); proj=perspective(60,240/200,0.1,100)
r.render(c,cube(1.5),multiply(proj,multiply(view,model))); c.save_png("docs/cube.png"); print("ok")
