import sys,wave,io,struct,math
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.audio import decode_wav,AudioPlayer
b=io.BytesIO(); w=wave.open(b,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(b'\x00\x00'*800); w.close(); d=decode_wav(b.getvalue()); print(d.channels,d.rate,d.bits,d.duration)
