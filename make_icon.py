from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
src = Image.open(r"D:\AI_Temp\AMFW\assets\amfw_icon.png").convert("RGBA")
bg = src.getpixel((128, 140))
out = src.copy()
draw = ImageDraw.Draw(out)
draw.rectangle([36, 138, 220, 184], fill=bg)
font_path = r"C:\Windows\Fonts\arialbd.ttf"
size = 42
while size > 20:
    font = ImageFont.truetype(font_path, size)
    box = draw.textbbox((0, 0), "AMFWX", font=font)
    width = box[2] - box[0]
    height = box[3] - box[1]
    if width <= 174:
        break
    size -= 1
x = (256 - width) / 2 - box[0]
y = 146 - box[1]
draw.text((x, y), "AMFWX", font=font, fill=(245, 248, 255, 255))
assets = Path("assets"); assets.mkdir(exist_ok=True)
out.save(assets / "AMFWX.png")
out.save(assets / "amfwx_icon.png")
sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]
out.save(assets / "AMFWX.ico", sizes=sizes)
out.save(assets / "amfwx_icon.ico", sizes=sizes)
print(size, width, height, assets / "AMFWX.ico")
