import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf",24)
print("gpos",len(f.gpos_pairs),"kern",len(f.kern),"AV",f.kerning(f.glyph_id("A"),f.glyph_id("V")))
