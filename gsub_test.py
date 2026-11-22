import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf", 24)
print("lig", len(f.ligatures), "fi", f.shape("fi"), "f", f.shape("f"))
