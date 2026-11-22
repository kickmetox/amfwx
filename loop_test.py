import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas,Color
from amfwx.sdl3_backend import Sdl3Loop
loop=Sdl3Loop(32,24,"loop",lambda w,h: Canvas(w,h,Color(10,20,30)))
loop.run(max_frames=2); print("ok")
