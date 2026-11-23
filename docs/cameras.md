# Cameras and webcams

## Inventory

```python
from amfwx import list_cameras, list_pnp_cameras

print(list_cameras())       # OpenCV/UVC indexes
print(list_pnp_cameras())   # Windows PnP camera names
```

The PnP list includes devices such as `OsmoAction4`, even when OpenCV cannot
open them as a UVC webcam.

## Webcam capture

```python
from amfwx import Webcam

cam = Webcam(0, width=1280, height=720, fps=30)
print(cam.settings())
frame = cam.read()
frame.save("frame.jpg")
cam.close()
```

Requires:

```powershell
pip install opencv-python-headless
```

Controls:

```python
cam.set_control("brightness", 0.5)
cam.set_control("exposure", -5)
```

## Tethering

```python
files = cam.tether("D:\\Captures", count=5, interval=2.0)
```

Chroma key during tethering:

```python
files = cam.tether("D:\\Captures", count=3, chroma_key=(0, 255, 0))
```

## GoPro

```python
from amfwx import GoProCamera

gopro = GoProCamera()       # 10.5.5.9:8080
print(gopro.status())
gopro.take_photo()
gopro.tether("D:\\Captures", count=3, interval=2.0)
```

## DSLR / system cameras via gPhoto2

Optional external CLI:

```python
from amfwx import GPhoto2Camera

camera = GPhoto2Camera()
print(camera.settings())
camera.capture("D:\\Captures")
```

This is the cross-vendor path for Canon, Nikon, Sony, Fuji, Olympus, Leica
and others supported by libgphoto2. It requires `gphoto2` on Windows.

## Chroma key

```python
from amfwx import chroma_key, composite

foreground = chroma_key(image, key=(0, 255, 0), tolerance=60)
result = composite(foreground, background)
```

## Vendor reality

| Vendor | Inventory | Capture | Tethering |
|---|---|---|---|
| Canon | PnP / gPhoto2 | UVC or gPhoto2 | gPhoto2 |
| Nikon | PnP / gPhoto2 | UVC or gPhoto2 | gPhoto2 |
| Sony | PnP / gPhoto2 | UVC or gPhoto2 | gPhoto2 |
| Fuji | PnP / gPhoto2 | UVC or gPhoto2 | gPhoto2 |
| Olympus | PnP / gPhoto2 | UVC or gPhoto2 | gPhoto2 |
| Leica | PnP / gPhoto2 | UVC or gPhoto2 | gPhoto2 |
| GoPro | HTTP | GoPro HTTP | GoPro HTTP |
| DJI | PnP / UVC | UVC if webcam mode | ❌ |

There is **no single native SDK** for all vendors. Vendor SDKs (Canon EDSDK,
Nikon SDK, Sony Camera Remote SDK, etc.) are not bundled.

## Camera window

```powershell
python -m amfwx --camera-ui
```

Snapshot, tethering, resolution and green-screen chroma key.

## MTP/PTP cameras

```powershell
python -m amfwx --list-mtp
python -m amfwx --mtp-download "D:\Photos" --mtp-device "OsmoAction4"
```

Uses the Windows Shell to access MTP/PTP camera storage. It supports JPEG, PNG, TIFF, HEIC, DNG, CR2, NEF, ARW, RAF and ORF. No vendor SDK needed.
