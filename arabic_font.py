import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
for p in [r"C:\Windows\Fonts\segoeui.ttf",r"C:\Windows\Fonts\arial.ttf",r"C:\Windows\Fonts\tahoma.ttf"]:
 try:
  f=TrueTypeFont(p)
  print(p, [(hex(c),f.glyph_id(chr(c))) for c in (0x0627,0x0644,0xFE8D,0xFE8E,0xFEFB)])
 except Exception as e: print(e)
