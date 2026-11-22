import sys,struct,io
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
# build tiny AVI with a 1x1 JPEG? use existing test JPEG base64
import base64
from tests.test_jpeg import JPEG
avih=struct.pack('<IIIIIIII',40000,0,0,0,1,0,16,16)+b'\x00'*32
strh=struct.pack('<4s4sIHHIIIIIIII',b'vids',b'MJPG',0,0,0,0,1,25,0,1,0,0xFFFFFFFF,0)
strf=struct.pack('<IiiHHIIiiII',40,16,16,1,24,0,16*16*3,0,0,0,0)
def chunk(n,d): return n+struct.pack('<I',len(d))+d+(b'\x00' if len(d)%2 else b'')
hdrl=chunk(b'avih',avih)+chunk(b'strh',strh)+chunk(b'strf',strf)
hdrl=b'LIST'+struct.pack('<I',len(hdrl)+4)+b'hdrl'+hdrl
movi=b'LIST'+struct.pack('<I',len(chunk(b'00dc',JPEG))+4)+b'movi'+chunk(b'00dc',JPEG)
body=b'AVI '+hdrl+movi
avi=b'RIFF'+struct.pack('<I',len(body))+body
from amfwx.video import AviVideo
v=AviVideo(avi); print(v.width,v.height,v.fps,len(v.frames),v.duration); print(v.frame(0).width)
