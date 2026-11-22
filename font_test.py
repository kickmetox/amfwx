import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
from amfwx import Canvas, Color
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf", 24)
print("glyphs", len(f.cmap), f.advance(f.glyph_id("A")))
c=Canvas(300,80,Color(20,22,28)); f.draw(c,"AMFWX hello",10,10,Color(255,255,255)); c.save_bmp("font.bmp"); print("ok")
