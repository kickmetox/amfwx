import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.canvas import Canvas,Color
from amfwx.webp import encode_webp,decode_webp
c=Canvas(8,6,Color(200,10,20)); data=encode_webp(c); print(len(data)); w,h,p=decode_webp(data); print(w,h,p[:4])
