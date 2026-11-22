import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas,Panel,Rect,Splitter
s=Splitter(); s.arrange(Rect(0,0,400,200)); d=s._divider(); s.mouse_down(d.x+1,d.y+1); s.mouse_move(300,100); print(s.ratio, s.second.rect.x); s.paint(Canvas(400,200))
