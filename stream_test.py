import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.mfvideo import MediaStream
s=MediaStream(r"C:\Users\Lenovo\Desktop\Demo2.mp4"); print(s.width,s.height); c=s.next_frame(); print(c.width if c else None); s.close()
