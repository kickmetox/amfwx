from amfwx.pdf_print import print_images
from PIL import Image,ImageDraw
im=Image.new('RGB',(800,1000),'white'); d=ImageDraw.Draw(im); d.text((60,60),'AMFWX GDI+ TEST 2',fill='black')
print(print_images([im],'ECOSYS M5521cdn','AMFWX GDI+ Test 2'))
