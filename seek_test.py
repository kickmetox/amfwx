import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import MediaStream
s=MediaStream(r"C:\Users\Lenovo\Desktop\Demo2.mp4"); s.seek(1.0); f=s.next_frame(); print(f.width if f else None); s.close()
