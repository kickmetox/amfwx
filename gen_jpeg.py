from PIL import Image
import io,base64
im=Image.new("RGB",(16,16),(255,0,0)); b=io.BytesIO(); im.save(b,"JPEG",quality=90); print(base64.b64encode(b.getvalue()).decode())
