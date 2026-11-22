import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.mfvideo import MediaVideo
v=MediaVideo(r"C:\Users\Lenovo\Desktop\Demo2.mp4"); c=v.frame(0); print(c.width,c.height,c.pixel(100,100))
