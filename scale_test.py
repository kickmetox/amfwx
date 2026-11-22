import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas,Color
c=Canvas(4,4,Color(100,50,20)); s=c.scaled(8,8); print(s.width,s.pixel(3,3)); print(c.crop(1,1,2,2).pixel(0,0), c.thumbnail(2).width)
