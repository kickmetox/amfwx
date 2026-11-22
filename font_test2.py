import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
from amfwx import Canvas, Color
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf", 28)
print("kern",len(f.kern), "A", f.glyph_id("A"), "Auml", f.glyph_id("Ä"))
c=Canvas(300,80,Color(20,22,28)); f.draw(c,"AVATAR Äpfel",8,8,Color(255,255,255)); c.save_png("docs/font2.png"); print("ok")
