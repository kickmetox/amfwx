from amfwx import AudioBuffer,Gain
b=AudioBuffer(1,8000,3); b.data=[[1,2,3]]; Gain(0.5).process(b); print(b.data)
