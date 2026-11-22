import sys,traceback
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.font import TrueTypeFont,_u16,_u32
f=TrueTypeFont(r"C:\Windows\Fonts\segoeui.ttf")
base=f.tables["GPOS"][0]; ll=base+_u16(f.data,base+8); n=_u16(f.data,ll)
count=0
for i in range(n):
 l=ll+_u16(f.data,ll+2+i*2); sc=_u16(f.data,l+4)
 for j in range(sc):
  s=l+_u16(f.data,l+6+j*2)
  if _u16(f.data,s)==1 and _u16(f.data,s+2)==4:
   offset=_u32(f.data,s+4); sub=s+offset
   try:
    f._parse_mark_base_subtable(sub); count+=1
   except Exception as e:
    print("ERR",hex(sub),e); traceback.print_exc(); break
print("parsed",count,"marks",len(f.mark_glyphs),"pos",len(f.mark_positions))
