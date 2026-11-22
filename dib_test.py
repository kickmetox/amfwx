import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas, Color, set_clipboard_image, get_clipboard_image
c=Canvas(4,4,Color(10,20,30)); print(set_clipboard_image(c)); d=get_clipboard_image(); print(d.width,d.height,d.pixel(1,2))
