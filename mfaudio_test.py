import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import MediaAudio
for p in [r"C:\Users\Lenovo\Desktop\Demo2.mp4", r"C:\Users\Lenovo\Videos\Bildschirmaufzeichnungen\Bildschirmaufnahme 2026-08-17 004537.mp4"]:
 try:
  a=MediaAudio.from_file(p,1); print(p.split("\\")[-1],a.rate,a.channels,a.bits,len(a.data))
 except Exception as e: print("ERR",p,e)
