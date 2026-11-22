import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window
w=Window("x",300,200); print("main",w.hwnd,"host",w.uia_host); w.close()
