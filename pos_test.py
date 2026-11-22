import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.audio import AudioPlayer,Wav
p=AudioPlayer(); w=Wav(1,8000,16,b'\x00\x00'*800); p.play(w); print(p.position()); p.stop()
