"""Optional SDL3 capability probe for AMFWX."""

from __future__ import annotations

import ctypes
import os
import sys


def probe_sdl3(path=None):
    if sys.platform != "win32":
        return {"available": False, "path": "", "features": {},
                "error": "only Windows"}
    candidates = [path] if path else []
    candidates += [os.environ.get("AMFWX_SDL3", ""),
                   os.path.join(os.path.dirname(__file__), "bin", "SDL3.dll"),
                   "SDL3.dll"]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            library = ctypes.WinDLL(candidate)
            return {
                "available": True,
                "path": candidate,
                "features": {
                    "window": hasattr(library, "SDL_CreateWindow"),
                    "events": hasattr(library, "SDL_PollEvent"),
                    "audio": hasattr(library, "SDL_OpenAudioDeviceStream"),
                    "gamepad": hasattr(library, "SDL_OpenGamepad"),
                    "gpu": hasattr(library, "SDL_CreateGPUDevice"),
                },
                "error": "",
            }
        except Exception:
            continue
    return {"available": False, "path": "", "features": {},
            "error": "SDL3.dll not found"}
