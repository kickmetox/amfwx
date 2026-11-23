from PIL import Image,ImageDraw
from amfwx.pdf_print import print_images
im=Image.new('RGB',(400,300),'white'); d=ImageDraw.Draw(im); d.text((20,20),'AMFWX GDI TEST',fill='black')
print(print_images([im],'ECOSYS M5521cdn','AMFWX GDI Test'))
