# Security hardening

## Native DLL integrity

`amfwx/bin/checksums.json` contains SHA-256 hashes for the shipped DLLs:

- `SDL3.dll`
- `libwebp.dll`
- `libsharpyuv.dll`
- `mfdecode.dll`
- `uia_provider.dll`
- `TWAINDSM.dll`
- `TWAINDSM32.dll`

Verify:

```powershell
python tools/verify_native.py
```

Expected:

```text
OK: 7 DLLs verifiziert
```

The manifest is not a signature. It detects accidental corruption or
replacement during packaging. For supply-chain integrity, sign the release
artifact or publish the manifest hash with the release.

## DLL loading

The project loads its own DLLs by absolute path:

- `amfwx/sdl3.py`
- `amfwx/webp.py`
- `amfwx/mfvideo.py`
- `amfwx/uia_native.py`

System DLLs (`user32`, `gdi32`, `winmm`, `uiautomationcore`,
`d3dcompiler_47`, ...) are loaded by name.

## Installer

The installer and uninstaller are tested with:

- silent install
- registry cleanup
- shortcut cleanup
- target cleanup

## Crash handling

`CrashLogger` writes rotating logs to:

```text
%LOCALAPPDATA%\AMFWX\crash.log
```

It does not upload data.

## Fuzzing

Deterministic fuzz tests cover:

- widgets
- MIDI/MP4/AVI/WAV/PNG/WebP/TrueType
- shaders
- resource packs

## Limits

- no public certificate; signing is a distributor responsibility
- no security certification
- Media Foundation remains a system codec
