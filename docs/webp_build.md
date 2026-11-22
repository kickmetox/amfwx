# WebP build

libwebp 1.5.0 wurde aus Quelltext mit Visual Studio 2022 Build Tools gebaut.

## Quellen

- https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-1.5.0.tar.gz
- SHA-256: `7d6fab70cf844bf6769077bd5d7a74893f8ffd4dfb42861745750c63c2a5c92c`

## Build

```powershell
cmake -S libwebp-1.5.0 -B vendor\webp-build `
  -G "Visual Studio 17 2022" -A x64 `
  -DBUILD_SHARED_LIBS=ON `
  -DWEBP_BUILD_CWEBP=OFF -DWEBP_BUILD_DWEBP=OFF `
  -DWEBP_BUILD_GIF2WEBP=OFF -DWEBP_BUILD_IMG2WEBP=OFF `
  -DWEBP_BUILD_VWEBP=OFF -DWEBP_BUILD_WEBPINFO=OFF `
  -DWEBP_BUILD_WEBPMUX=OFF -DWEBP_BUILD_EXTRAS=OFF

cmake --build vendor\webp-build --config Release --target webp
```

## Installiert

- `amfwx/bin/libwebp.dll`
- `amfwx/bin/libsharpyuv.dll`
- `amfwx/bin/LICENSE-libwebp.txt`

## API

```python
from amfwx import decode_webp, encode_webp

data = encode_webp(canvas)
width, height, pixels = decode_webp(data)
```
