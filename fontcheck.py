import sys,glob,os
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont
for p in [r"C:\Windows\Fonts\calibri.ttf",r"C:\Windows\Fonts\arial.ttf",r"C:\Windows\Fonts\times.ttf",r"C:\Windows\Fonts\segoeui.ttf"]:
 if os.path.exists(p):
  try:
   f=TrueTypeFont(p); print(os.path.basename(p),len(f.gpos_pairs),len(f.gpos_class_tables))
  except Exception as e: print(e)
