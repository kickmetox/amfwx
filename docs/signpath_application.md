# SignPath Foundation application

Use this text for the SignPath application. Replace `<GITHUB-USER>` with
your GitHub account or organization.

## Project

- **Name:** AMFWX
- **Repository:** `https://github.com/<GITHUB-USER>/amfwx`
- **Homepage:** same as repository (a separate website is not required)
- **License:** MIT
- **Language:** Python (ctypes), C++ for small native helpers
- **Platform:** Windows 10/11 x86-64

## Description

AMFWX is an independent, Windows-only desktop UI framework written in pure
Python. It provides its own software rasterizer, widgets, Win32 event loop,
text shaping, accessibility providers, media decoding and an installer.
It does not wrap Qt, GTK, wxWidgets or a browser engine.

## Build

The release workflow builds:

```text
python -m pip install .
powershell -ExecutionPolicy Bypass -File tools/build_app.ps1
python tools/build_own_installer.py
```

Artifact to sign:

```text
dist/AMFWX-Own-Setup-*.exe
```

## Release workflow

`.github/workflows/signpath.yml`

## Signing configuration

- Project slug: `amfwx`
- Signing policy slug: `release-signing`
- Artifact configuration slug: `amfwx-installer`
- Artifact configuration file: `signpath/artifact-configuration.xml`

## Security

- no telemetry
- no network access at runtime
- no embedded browser
- native DLL sources and build instructions are in the repository
- see `SECURITY.md`

## Notes

SignPath Foundation is the publisher of the signed binary. This is expected
for the free open-source signing program.
