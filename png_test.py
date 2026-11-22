import sys, tempfile
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Canvas, Color
from amfwx.png import decode_png, encode_png
c=Canvas(20,10,Color(0,0,0)); c.fill_rect(__import__("amfwx").Rect(2,2,5,4),Color(255,0,0))
p=tempfile.NamedTemporaryFile(suffix=".png",delete=False).name
c.save_png(p); d=Canvas.from_png(p); print(d.pixel(3,3),d.width,d.height)
from PIL import Image
im=Image.open(p); print(im.size, im.getpixel((3,3)))
