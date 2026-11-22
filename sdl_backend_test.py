import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.canvas import Canvas,Color
from amfwx.sdl3_backend import Sdl3Renderer
try:
 r=Sdl3Renderer(64,48,"test"); c=Canvas(64,48,Color(200,10,20)); r.present(c); print("present ok"); r.close()
except Exception as e: print("ERR",e)
