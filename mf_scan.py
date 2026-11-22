import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.mfvideo import MediaVideo
v=MediaVideo(r"C:\Users\Lenovo\Desktop\Demo2.mp4"); c=v.frame(0)
print(c.width,c.height, sum(1 for y in range(0,200,10) for x in range(0,200,10) if c.pixel(x,y)!=__import__('amfwx').Color(0,0,0)))
