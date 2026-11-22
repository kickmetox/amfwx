"""HLSL → DXBC shader compilation through d3dcompiler_47."""

from __future__ import annotations

import ctypes
from ctypes import POINTER, byref, c_char_p, c_size_t, c_uint, c_void_p

_compiler = None


class ShaderError(RuntimeError):
    pass


def _library():
    global _compiler
    if _compiler is not None:
        return _compiler
    library = ctypes.WinDLL("d3dcompiler_47")
    library.D3DCompile.argtypes = [
        c_void_p, c_size_t, c_char_p, c_void_p, c_void_p, c_char_p, c_char_p,
        c_uint, c_uint, POINTER(c_void_p), POINTER(c_void_p)]
    library.D3DCompile.restype = ctypes.c_long
    _compiler = library
    return library


def _blob_bytes(blob):
    table = ctypes.cast(blob, POINTER(POINTER(c_void_p))).contents
    get_pointer = ctypes.WINFUNCTYPE(c_void_p, c_void_p)(table[3])
    get_size = ctypes.WINFUNCTYPE(c_size_t, c_void_p)(table[4])
    release = ctypes.WINFUNCTYPE(c_uint, c_void_p)(table[2])
    try:
        size = get_size(blob)
        return ctypes.string_at(get_pointer(blob), size)
    finally:
        release(blob)


def compile_hlsl(source, entry="main", target="cs_5_0", flags=0):
    library = _library()
    source_bytes = source.encode("utf-8")
    code = c_void_p()
    errors = c_void_p()
    result = library.D3DCompile(
        source_bytes, len(source_bytes), b"amfwx.hlsl", None, None,
        entry.encode("utf-8"), target.encode("utf-8"), flags, 0,
        byref(code), byref(errors))
    if result < 0:
        message = ""
        if errors:
            try:
                message = _blob_bytes(errors).decode("utf-8", "replace")
            except Exception:
                pass
        raise ShaderError(f"D3DCompile 0x{result & 0xFFFFFFFF:08X}: {message}")
    if errors:
        _blob_bytes(errors)
    return _blob_bytes(code)


def compile_dxil(source, entry="main", target="cs_6_0"):
    import os
    import subprocess
    import tempfile
    from pathlib import Path
    candidates = [
        os.environ.get("AMFWX_DXC", ""),
        str(Path(tempfile.gettempdir()) / "dxc" / "build" / "native" / "bin" / "x64" / "dxc.exe"),
    ]
    dxc = next((item for item in candidates if item and Path(item).exists()), None)
    if dxc is None:
        raise ShaderError("dxc.exe nicht gefunden")
    with tempfile.TemporaryDirectory() as folder:
        source_path = Path(folder) / "shader.hlsl"
        output_path = Path(folder) / "shader.dxil"
        source_path.write_text(source, encoding="utf-8")
        result = subprocess.run([dxc, "-T", target, "-E", entry, str(source_path),
                                 "-Fo", str(output_path)],
                                capture_output=True, text=True)
        if result.returncode:
            raise ShaderError(result.stderr or result.stdout)
        return output_path.read_bytes()
