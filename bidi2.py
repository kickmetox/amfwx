import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.bidi import bidi_reorder
for s in ["abc مرحبا def","مرحبا abc","hello","שלום world","abc 123 def"]:
 print(ascii(s),"->",ascii(bidi_reorder(s)))
