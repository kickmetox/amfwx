# H.264/MP4 über Media Foundation

## Native DLL

`native/mfdecode.cpp` wird mit MSVC gebaut:

```powershell
cl /nologo /LD /EHsc ^
  /I "%TEMP%\sdkcpp\c\Include\10.0.26100.0\um" ^
  /I "%TEMP%\sdkcpp\c\Include\10.0.26100.0\shared" ^
  /I "%TEMP%\sdkcpp\c\Include\10.0.26100.0\ucrt" ^
  native\mfdecode.cpp ^
  /link /LIBPATH:"%TEMP%\sdkcpp_x64\c\um\x64" ^
  /OUT:amfwx\bin\mfdecode.dll
```

Abhängigkeiten: `mfplat.lib`, `mfreadwrite.lib`, `mfuuid.lib`, `ole32.lib`.

## Python

```python
from amfwx import MediaVideo

video = MediaVideo.from_file("video.mp4")
canvas = video.frame(0)
```

## Technik

- Media Foundation Source Reader
- Ausgabe: NV12
- Umwandlung: NV12 → BGRA
- Auflösung: 4K getestet
- Erstes Bild: 3840×2160

## Grenzen

- Frames werden einzeln dekodiert (kein kontinuierlicher Decoder)
- kein Audio
- kein Streaming
- kein Hardware-Decoder erzwungen
- kein FPS aus dem Container
