import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.arabic import arabic_shape
from amfwx.bidi import bidi_reorder
s="سلام"
print([hex(ord(c)) for c in arabic_shape(s)])
print([hex(ord(c)) for c in bidi_reorder(arabic_shape(s))])
