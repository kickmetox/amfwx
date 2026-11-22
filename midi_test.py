import struct
from amfwx import MidiFile
header=b'MThd'+struct.pack('>IHHH',6,0,1,480)
track=b'\x00\x90\x3c\x64\x83\x60\x80\x3c\x00\x00\xff\x2f\x00'
data=header+b'MTrk'+struct.pack('>I',len(track))+track
m=MidiFile(data); print(m.notes, m.duration)
