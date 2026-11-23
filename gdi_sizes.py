from PIL import Image,ImageDraw
from amfwx.pdf_print import print_images
for size in ((800,1200),(1200,1600),(1600,2200)):
    im=Image.new('RGB',size,'white'); d=ImageDraw.Draw(im); d.text((20,20),'AMFWX GDI',fill='black')
    try:
        print(size, print_images([im],'ECOSYS M5521cdn','AMFWX GDI '+str(size)))
    except Exception as e:
        print(size,'ERR',type(e).__name__,e)
