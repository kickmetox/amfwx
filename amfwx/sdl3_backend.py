"""Minimal SDL3 window/renderer backend for AMFWX."""

from __future__ import annotations

import ctypes
import os
from ctypes import c_int, c_uint, c_void_p, c_char_p, POINTER

from .canvas import Canvas

SDL_INIT_VIDEO = 0x00000020
SDL_PIXELFORMAT_BGRA8888 = 0x16862004
SDL_TEXTUREACCESS_STREAMING = 1
SDL_WINDOW_RESIZABLE = 0x00000020
SDL_EVENT_QUIT = 0x100
SDL_EVENT_KEY_DOWN = 0x300
SDL_EVENT_MOUSE_MOTION = 0x400


class Sdl3Error(RuntimeError):
    pass


class Sdl3Renderer:
    def __init__(self, width, height, title="AMFWX SDL3"):
        from .sdl3 import probe_sdl3
        probe = probe_sdl3()
        if not probe.get("available"):
            raise Sdl3Error(probe.get("error", "SDL3 nicht verfügbar"))
        self.library = ctypes.WinDLL(probe["path"])
        self.width = int(width)
        self.height = int(height)
        self.window = None
        self.renderer = None
        self.texture = None
        self._configure()
        if not self.library.SDL_Init(SDL_INIT_VIDEO):
            raise Sdl3Error(self._error("SDL_Init"))
        self.window = self.library.SDL_CreateWindow(
            title.encode("utf-8"), self.width, self.height,
            SDL_WINDOW_RESIZABLE)
        if not self.window:
            raise Sdl3Error(self._error("SDL_CreateWindow"))
        self.renderer = self.library.SDL_CreateRenderer(self.window, None)
        if not self.renderer:
            raise Sdl3Error(self._error("SDL_CreateRenderer"))
        self.texture = self.library.SDL_CreateTexture(
            self.renderer, SDL_PIXELFORMAT_BGRA8888,
            SDL_TEXTUREACCESS_STREAMING, self.width, self.height)
        if not self.texture:
            raise Sdl3Error(self._error("SDL_CreateTexture"))

    def _configure(self):
        lib = self.library
        lib.SDL_Init.argtypes = [c_uint]
        lib.SDL_Init.restype = ctypes.c_bool
        lib.SDL_CreateWindow.argtypes = [c_char_p, c_int, c_int,
                                         ctypes.c_uint64]
        lib.SDL_CreateWindow.restype = c_void_p
        lib.SDL_CreateRenderer.argtypes = [c_void_p, c_char_p]
        lib.SDL_CreateRenderer.restype = c_void_p
        lib.SDL_CreateTexture.argtypes = [c_void_p, c_uint, c_int, c_int,
                                          c_int]
        lib.SDL_CreateTexture.restype = c_void_p
        lib.SDL_UpdateTexture.argtypes = [c_void_p, c_void_p, c_void_p,
                                          c_int]
        lib.SDL_UpdateTexture.restype = ctypes.c_bool
        lib.SDL_RenderClear.argtypes = [c_void_p]
        lib.SDL_RenderClear.restype = ctypes.c_bool
        lib.SDL_RenderTexture.argtypes = [c_void_p, c_void_p, c_void_p,
                                          c_void_p]
        lib.SDL_RenderTexture.restype = ctypes.c_bool
        lib.SDL_RenderPresent.argtypes = [c_void_p]
        lib.SDL_RenderPresent.restype = None
        lib.SDL_PollEvent.argtypes = [c_void_p]
        lib.SDL_PollEvent.restype = ctypes.c_bool
        lib.SDL_DestroyTexture.argtypes = [c_void_p]
        lib.SDL_DestroyRenderer.argtypes = [c_void_p]
        lib.SDL_DestroyWindow.argtypes = [c_void_p]
        lib.SDL_Quit.argtypes = []
        lib.SDL_GetError.restype = c_char_p
        lib.SDL_GetCurrentVideoDriver.restype = c_char_p
        lib.SDL_GetRendererName.argtypes = [c_void_p]
        lib.SDL_GetRendererName.restype = c_char_p

    def _error(self, where):
        message = self.library.SDL_GetError()
        return f"{where}: {message.decode('utf-8', 'replace') if message else 'unknown'}"

    def backend_info(self):
        driver = self.library.SDL_GetCurrentVideoDriver()
        renderer = self.library.SDL_GetRendererName(self.renderer)
        renderer_name = (renderer.decode("utf-8", "replace")
                         if renderer else "unknown")
        return {
            "video_driver": (driver.decode("utf-8", "replace")
                             if driver else "unknown"),
            "renderer": renderer_name,
            "hardware": renderer_name not in ("software", "unknown"),
        }

    def present(self, canvas=None):
        canvas = canvas or Canvas(self.width, self.height)
        if (canvas.width, canvas.height) != (self.width, self.height):
            self.width, self.height = canvas.width, canvas.height
            self.library.SDL_DestroyTexture(self.texture)
            self.texture = self.library.SDL_CreateTexture(
                self.renderer, SDL_PIXELFORMAT_BGRA8888,
                SDL_TEXTUREACCESS_STREAMING, self.width, self.height)
        data = (ctypes.c_ubyte * len(canvas.data)).from_buffer(canvas.data)
        if not self.library.SDL_UpdateTexture(self.texture, None, data,
                                               self.width * 4):
            raise Sdl3Error(self._error("SDL_UpdateTexture"))
        self.library.SDL_RenderClear(self.renderer)
        self.library.SDL_RenderTexture(self.renderer, self.texture,
                                       None, None)
        self.library.SDL_RenderPresent(self.renderer)

    def poll(self):
        event = (ctypes.c_ubyte * 256)()
        events = []
        while self.library.SDL_PollEvent(event):
            events.append(bytes(event[:32]))
        return events

    def close(self):
        if self.texture:
            self.library.SDL_DestroyTexture(self.texture)
            self.texture = None
        if self.renderer:
            self.library.SDL_DestroyRenderer(self.renderer)
            self.renderer = None
        if self.window:
            self.library.SDL_DestroyWindow(self.window)
            self.window = None
        self.library.SDL_Quit()

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()


class Sdl3Loop:
    """Small SDL3 frame/event loop independent from the Win32 Window loop."""

    def __init__(self, width, height, title, paint, on_event=None):
        self.renderer = Sdl3Renderer(width, height, title)
        self.paint = paint
        self.on_event = on_event
        self.running = True

    def step(self):
        canvas = self.paint(self.renderer.width, self.renderer.height)
        self.renderer.present(canvas)
        for raw in self.renderer.poll():
            event_type = int.from_bytes(raw[:4], "little")
            if self.on_event is not None:
                self.on_event(event_type, raw)
            if event_type == SDL_EVENT_QUIT:
                self.running = False

    def run(self, max_frames=None):
        frames = 0
        while self.running:
            self.step()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
        self.renderer.close()

    def close(self):
        self.renderer.close()
