import sys,tempfile
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from PIL import Image
from amfwx import Canvas, Color
im=Image.new("RGB",(32,32),(255,0,0)); p=tempfile.NamedTemporaryFile(suffix=".jpg",delete=False).name; im.save(p,"JPEG",quality=95)
c=Canvas.from_jpeg(p); print(c.width,c.height,c.pixel(16,16)); 
im2=Image.new("RGB",(16,16),(0,0,0));
