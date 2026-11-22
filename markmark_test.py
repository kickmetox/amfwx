import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf",24)
print("markmark",len(f.mark_mark_positions))
print(f.positioned("a\u0301\u0302"))
