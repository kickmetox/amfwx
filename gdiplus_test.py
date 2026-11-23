from amfwx.pdf_print import print_images
from PIL import Image,ImageDraw
im=Image.new('RGB',(800,1000),'white'); ImageDraw.Draw(im).text((40,40),'AMFWX GDI+ TEST',fill='black')
print(print_images([im],'ECOSYS M5521cdn','AMFWX GDI+ Test'))
