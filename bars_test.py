import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas,Rect,StatusBar,ToolBar
s=StatusBar(["a","b"]); s.arrange(Rect(0,0,200,24)); s.paint(Canvas(200,24)); t=ToolBar([("X",lambda:None)]); t.arrange(Rect(0,0,200,34)); t.paint(Canvas(200,34)); print("ok")
