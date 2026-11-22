import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf",24)
print("f gid",f.glyph_id("f"),"i",f.glyph_id("i"))
print("keys",list(f.ligatures)[:10])
print("cand f",f.ligatures.get(f.glyph_id("f")))
