import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.arabic import arabic_shape
for s in ["لا","بلا","لآ","لأ","لإ"]:
 print(ascii(s),"->",[hex(ord(c)) for c in arabic_shape(s)])
