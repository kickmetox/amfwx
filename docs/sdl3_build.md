# SDL3 aus Quelltext bauen

AMFWX baut SDL3 3.4.20 mit Visual Studio 2022 Build Tools.

## Voraussetzungen

- Visual Studio 2022 Build Tools
- MSVC 14.44
- CMake 3.31

## Quellen

- https://github.com/libsdl-org/SDL/releases/tag/release-3.4.20
- `SDL3-3.4.20.tar.gz`
- SHA-256: `f3bb06f55bed9557227a700af2ea62e49497ebdf58037732a731a5fb3ef8581f`

## Build

```powershell
cmake -S SDL3-3.4.20 -B vendor\sdl3-build `
  -G "Visual Studio 17 2022" -A x64 `
  -DSDL_SHARED=ON -DSDL_STATIC=OFF `
  -DSDL_TEST_LIBRARY=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF

cmake --build vendor\sdl3-build --config Release --target SDL3-shared
```

Ergebnis:

```text
vendor\sdl3-build\Release\SDL3.dll
```

Installiert als:

```text
amfwx\bin\SDL3.dll
```

SHA-256 des eigenen Builds:

```text
F00422D94EC12D68A65CFFD6FFE5AB47D7CCBA8984439A24703EBF9A67701132
```

## Lizenz

SDL3 steht unter der zlib-Lizenz. Die Lizenz liegt bei:

```text
amfwx\bin\LICENSE-SDL3.txt
```

## Status

`probe_sdl3()` erkennt die DLL:

```text
available: True
window: True
events: True
audio: True
gamepad: True
gpu: True
```

Der SDL3-Renderer ist implementiert in `amfwx/sdl3_backend.py`:

* `Sdl3Renderer`
* Fenster
* BGRA-Streaming-Textur
* `present(canvas)`
* `poll()`
* `close()`

## Eventloop

```python
from amfwx import Canvas, Color, Sdl3Loop

loop = Sdl3Loop(640, 480, "AMFWX",
                lambda w, h: Canvas(w, h, Color(24, 26, 32)))
loop.run()
```
