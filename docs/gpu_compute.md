# GPU-Compute-Schicht

## Vorhanden

- HLSL -> DXBC via d3dcompiler_47
- HLSL -> DXIL via dxc
- amfwx/shaders.py
- amfwx/gpu.py
- SDL_GPU-Device direct3d12
- Storage-Buffer, Dispatch, Copy, Readback

## Status

GPU-Compute funktioniert:

```text
driver: direct3d12
result: (1.0, 0.0, 0.0, 1.0)
```

Wichtig:

* RW-Storage-Ressourcen liegen in `register(u0, space1)`.
* Readback ueber `SDL_DownloadFromGPUBuffer`.
* `SDL_CopyGPUBufferToBuffer` ist fuer Transfer-Buffer falsch.
