import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf", 24)
print("tables", "GSUB" in f.tables, f.tables.get("GSUB"))
print("cmap f", f.glyph_id("f"), "i",f.glyph_id("i"))
