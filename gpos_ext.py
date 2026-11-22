import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont,_u16,_u32
from collections import Counter
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf")
base=f.tables["GPOS"][0]; ll=base+_u16(f.data,base+8); n=_u16(f.data,ll)
c=Counter()
for i in range(n):
 l=ll+_u16(f.data,ll+2+i*2); st=_u16(f.data,l); sc=_u16(f.data,l+4)
 for j in range(sc):
  s=l+_u16(f.data,l+6+j*2)
  if _u16(f.data,s)==1:
   c[_u16(f.data,s+2)]+=1
print(c)
