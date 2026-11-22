import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import MediaAudioStream
s=MediaAudioStream(r"C:\Users\Lenovo\Desktop\Demo2.mp4"); print(s.rate,s.channels,s.bits,len(s.next_chunk())); s.close()
