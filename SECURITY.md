# Security Policy

## Supported versions

Security fixes are applied to the latest release on the default branch.

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Use GitHub's private vulnerability reporting:

1. Open the repository on GitHub.
2. Go to **Security** → **Advisories**.
3. Choose **Report a vulnerability**.

Include:

- affected version
- reproduction steps
- impact
- whether the issue requires a malicious file or local access

## Scope

AMFWX is a Windows desktop framework written in Python and ctypes.
Relevant areas:

- native DLL loading
- file parsers (PNG, WebP, MP4, AVI, MIDI, TrueType)
- installer/uninstaller
- accessibility proxies and UIA/MSAA hosting

## Not a guarantee

AMFWX is not certified for safety-, medical-, automotive- or
security-critical systems.
