import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas,Color,ImageView
c=Canvas(8,8,Color(200,0,0)); v=ImageView(c); v.arrange(__import__("amfwx").Rect(0,0,100,100)); out=Canvas(100,100); v.paint(out); print(out.pixel(50,50)); v.wheel(1); print(v.zoom)
