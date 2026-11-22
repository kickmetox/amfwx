import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import AudioQueuePlayer
p=AudioQueuePlayer(1,8000,16); p.feed(b'\x00\x00'*800); p.wait(); p.stop(); print("ok")
