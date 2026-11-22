import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.sdl3_backend import Sdl3Renderer
r=Sdl3Renderer(64,48); print(r.backend_info()); r.close()
