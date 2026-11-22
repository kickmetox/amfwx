import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf",24)
print("marks",len(f.mark_glyphs),"bases",len(f.base_glyphs),"positions",len(f.mark_positions))
print("a+mark",f.positioned("a\u0301"))
