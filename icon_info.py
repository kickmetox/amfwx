from PIL import Image
im=Image.open(r"D:\AI_Temp\AMFW\assets\amfw_icon.png").convert("RGBA")
for p in [(128,130),(128,140),(30,160),(128,110),(20,128),(128,220)]: print(p, im.getpixel(p))
# bbox of near-white pixels
px=im.load(); xs=[];ys=[]
for y in range(120,230):
 for x in range(20,236):
  r,g,b,a=px[x,y]
  if r>220 and g>220 and b>220:
   xs.append(x);ys.append(y)
print('white bbox', min(xs),min(ys),max(xs),max(ys))
