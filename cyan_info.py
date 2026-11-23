from PIL import Image
im=Image.open(r"D:\AI_Temp\AMFW\assets\amfw_icon.png").convert("RGBA"); px=im.load()
for y in range(175,235):
 xs=[x for x in range(20,236) if px[x,y][2]>120 and px[x,y][1]>120 and px[x,y][0]<120]
 if xs: print(y,min(xs),max(xs),px[xs[0],y])
