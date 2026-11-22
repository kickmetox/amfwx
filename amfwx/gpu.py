"""SDL_GPU compute pipeline bound via ctypes (DXBC shaders)."""

from __future__ import annotations

import ctypes
from ctypes import POINTER, byref, c_char_p, c_size_t, c_uint, c_void_p

from .shaders import compile_dxil
from .sdl3 import probe_sdl3

SHADERFORMAT_DXBC = 1 << 2
SHADERFORMAT_DXIL = 1 << 3
TRANSFER_DOWNLOAD = 1
BUFFER_COMPUTE_STORAGE_WRITE = (1 << 5) | (1 << 4)


class GPUShaderCreateInfo(ctypes.Structure):
    _fields_ = [
        ("code_size", c_size_t), ("code", c_void_p), ("entrypoint", c_char_p),
        ("format", c_uint), ("stage", c_uint), ("num_samplers", c_uint),
        ("num_storage_textures", c_uint), ("num_storage_buffers", c_uint),
        ("num_uniform_buffers", c_uint), ("props", c_uint),
    ]


class GPUComputePipelineCreateInfo(ctypes.Structure):
    _fields_ = [
        ("code_size", c_size_t), ("code", c_void_p), ("entrypoint", c_char_p),
        ("format", c_uint), ("num_samplers", c_uint),
        ("num_readonly_storage_textures", c_uint),
        ("num_readonly_storage_buffers", c_uint),
        ("num_readwrite_storage_textures", c_uint),
        ("num_readwrite_storage_buffers", c_uint),
        ("num_uniform_buffers", c_uint),
        ("threadcount_x", c_uint), ("threadcount_y", c_uint),
        ("threadcount_z", c_uint), ("props", c_uint),
    ]


class GPUBufferCreateInfo(ctypes.Structure):
    _fields_ = [("usage", c_uint), ("size", c_uint), ("props", c_uint)]


class GPUTransferBufferCreateInfo(ctypes.Structure):
    _fields_ = [("usage", c_uint), ("size", c_uint), ("props", c_uint)]


class GPUBufferLocation(ctypes.Structure):
    _fields_ = [("buffer", c_void_p), ("offset", c_uint)]


class GPUBufferRegion(ctypes.Structure):
    _fields_ = [("buffer", c_void_p), ("offset", c_uint), ("size", c_uint)]


class GPUTransferBufferLocation(ctypes.Structure):
    _fields_ = [("transfer_buffer", c_void_p), ("offset", c_uint)]


class StorageBufferBinding(ctypes.Structure):
    _fields_ = [("buffer", c_void_p), ("cycle", ctypes.c_bool),
                ("padding1", ctypes.c_ubyte), ("padding2", ctypes.c_ubyte),
                ("padding3", ctypes.c_ubyte)]


class GPUCompute:
    def __init__(self, driver=None):
        probe = probe_sdl3()
        if not probe.get("available"):
            raise RuntimeError(probe.get("error", "SDL3 nicht verfügbar"))
        self.library = ctypes.WinDLL(probe["path"])
        self._configure()
        if not self.library.SDL_Init(0x20):
            raise RuntimeError(self._error("SDL_Init"))
        self.device = self.library.SDL_CreateGPUDevice(
            SHADERFORMAT_DXIL, False, driver.encode("utf-8") if driver else None)
        if not self.device:
            raise RuntimeError(self._error("SDL_CreateGPUDevice"))

    def _configure(self):
        lib = self.library
        lib.SDL_Init.argtypes = [c_uint]
        lib.SDL_Init.restype = ctypes.c_bool
        lib.SDL_CreateGPUDevice.argtypes = [c_uint, ctypes.c_bool, c_char_p]
        lib.SDL_CreateGPUDevice.restype = c_void_p
        lib.SDL_Quit.argtypes = []
        lib.SDL_GetGPUDeviceDriver.argtypes = [c_void_p]
        lib.SDL_GetGPUDeviceDriver.restype = c_char_p
        lib.SDL_CreateGPUComputePipeline.argtypes = [
            c_void_p, POINTER(GPUComputePipelineCreateInfo)]
        lib.SDL_CreateGPUComputePipeline.restype = c_void_p
        lib.SDL_CreateGPUBuffer.argtypes = [c_void_p,
                                            POINTER(GPUBufferCreateInfo)]
        lib.SDL_CreateGPUBuffer.restype = c_void_p
        lib.SDL_CreateGPUTransferBuffer.argtypes = [
            c_void_p, POINTER(GPUTransferBufferCreateInfo)]
        lib.SDL_CreateGPUTransferBuffer.restype = c_void_p
        lib.SDL_AcquireGPUCommandBuffer.argtypes = [c_void_p]
        lib.SDL_AcquireGPUCommandBuffer.restype = c_void_p
        lib.SDL_BeginGPUComputePass.argtypes = [
            c_void_p, c_void_p, c_uint, c_void_p, c_uint]
        lib.SDL_BeginGPUComputePass.restype = c_void_p
        lib.SDL_BindGPUComputePipeline.argtypes = [c_void_p, c_void_p]
        lib.SDL_DispatchGPUCompute.argtypes = [c_void_p, c_uint, c_uint,
                                               c_uint]
        lib.SDL_EndGPUComputePass.argtypes = [c_void_p]
        lib.SDL_BeginGPUCopyPass.argtypes = [c_void_p]
        lib.SDL_BeginGPUCopyPass.restype = c_void_p
        lib.SDL_DownloadFromGPUBuffer.argtypes = [
            c_void_p, POINTER(GPUBufferRegion),
            POINTER(GPUTransferBufferLocation)]
        lib.SDL_EndGPUCopyPass.argtypes = [c_void_p]
        lib.SDL_SubmitGPUCommandBuffer.argtypes = [c_void_p]
        lib.SDL_SubmitGPUCommandBuffer.restype = ctypes.c_bool
        lib.SDL_WaitForGPUIdle.argtypes = [c_void_p]
        lib.SDL_MapGPUTransferBuffer.argtypes = [c_void_p, c_void_p,
                                                 ctypes.c_bool]
        lib.SDL_MapGPUTransferBuffer.restype = c_void_p
        lib.SDL_UnmapGPUTransferBuffer.argtypes = [c_void_p, c_void_p]
        lib.SDL_ReleaseGPUBuffer.argtypes = [c_void_p, c_void_p]
        lib.SDL_ReleaseGPUTransferBuffer.argtypes = [c_void_p, c_void_p]
        lib.SDL_ReleaseGPUComputePipeline.argtypes = [c_void_p, c_void_p]
        lib.SDL_DestroyGPUDevice.argtypes = [c_void_p]
        lib.SDL_GetError.restype = c_char_p

    def _error(self, where):
        message = self.library.SDL_GetError()
        return f"{where}: {message.decode('utf-8', 'replace') if message else 'unknown'}"

    def driver(self):
        value = self.library.SDL_GetGPUDeviceDriver(self.device)
        return value.decode("utf-8", "replace") if value else ""

    def run_compute(self, source, count=64, entry="main"):
        blob = compile_dxil(source, entry=entry, target="cs_6_0")
        code = ctypes.create_string_buffer(blob, len(blob))
        info = GPUComputePipelineCreateInfo()
        info.code_size = len(blob)
        info.code = ctypes.cast(code, c_void_p)
        info.entrypoint = entry.encode("utf-8")
        info.format = SHADERFORMAT_DXIL
        info.num_readwrite_storage_buffers = 1
        info.threadcount_x = count
        info.threadcount_y = 1
        info.threadcount_z = 1
        pipeline = self.library.SDL_CreateGPUComputePipeline(
            self.device, byref(info))
        if not pipeline:
            raise RuntimeError(self._error("SDL_CreateGPUComputePipeline"))
        size = count * 16
        buffer_info = GPUBufferCreateInfo(BUFFER_COMPUTE_STORAGE_WRITE, size, 0)
        gpu_buffer = self.library.SDL_CreateGPUBuffer(self.device,
                                                      byref(buffer_info))
        transfer_info = GPUTransferBufferCreateInfo(TRANSFER_DOWNLOAD, size, 0)
        transfer = self.library.SDL_CreateGPUTransferBuffer(
            self.device, byref(transfer_info))
        if not gpu_buffer or not transfer:
            raise RuntimeError(self._error("GPUBuffer/TransferBuffer"))
        command = self.library.SDL_AcquireGPUCommandBuffer(self.device)
        if not command:
            raise RuntimeError(self._error("SDL_AcquireGPUCommandBuffer"))
        binding = StorageBufferBinding(gpu_buffer, False, 0, 0, 0)
        pass_handle = self.library.SDL_BeginGPUComputePass(
            command, None, 0, byref(binding), 1)
        self.library.SDL_BindGPUComputePipeline(pass_handle, pipeline)
        self.library.SDL_DispatchGPUCompute(pass_handle, 1, 1, 1)
        self.library.SDL_EndGPUComputePass(pass_handle)
        copy = self.library.SDL_BeginGPUCopyPass(command)
        source_region = GPUBufferRegion(gpu_buffer, 0, size)
        target_location = GPUTransferBufferLocation(transfer, 0)
        self.library.SDL_DownloadFromGPUBuffer(copy, byref(source_region),
                                               byref(target_location))
        self.library.SDL_EndGPUCopyPass(copy)
        if not self.library.SDL_SubmitGPUCommandBuffer(command):
            raise RuntimeError(self._error("SDL_SubmitGPUCommandBuffer"))
        self.library.SDL_WaitForGPUIdle(self.device)
        pointer = self.library.SDL_MapGPUTransferBuffer(self.device, transfer,
                                                        False)
        if not pointer:
            raise RuntimeError(self._error("SDL_MapGPUTransferBuffer"))
        try:
            data = ctypes.string_at(pointer, size)
        finally:
            self.library.SDL_UnmapGPUTransferBuffer(self.device, transfer)
        self.library.SDL_ReleaseGPUBuffer(self.device, gpu_buffer)
        self.library.SDL_ReleaseGPUTransferBuffer(self.device, transfer)
        self.library.SDL_ReleaseGPUComputePipeline(self.device, pipeline)
        return data

    def close(self):
        if getattr(self, "device", None):
            self.library.SDL_DestroyGPUDevice(self.device)
            self.device = None
            self.library.SDL_Quit()
