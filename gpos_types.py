import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont,_u16,_u32
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf")
base=f.tables["GPOS"][0]; ll=base+_u16(f.data,base+8); n=_u16(f.data,ll)
print("lookups",n)
from collections import Counter
c=Counter()
for i in range(n):
 l=ll+_u16(f.data,ll+2+i*2); c[_u16(f.data,l)]+=1
print(c)
