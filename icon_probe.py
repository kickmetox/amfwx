from PIL import Image
from pathlib import Path
for f in [r"D:\AI_Temp\AMFW\assets\amfw_icon.png", r"D:\AI_Temp\AMFW\assets\amfw_icon.ico", r"D:\AI_Temp\AMFW\assets\AMFW.ico"]:
 im=Image.open(f); print(f, im.size, im.mode, getattr(im,'n_frames',1))
