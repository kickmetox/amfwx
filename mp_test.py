import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.mediaplayer import MediaPlayer
p=MediaPlayer(r"C:\Users\Lenovo\Desktop\Demo2.mp4",with_audio=False); p.play(); f=p.advance(0.04); print(f.width if f else None); p.close()
