# AMFWX 4.7.2

Bind GDI+ signatures explicitly.

## Fix

- `GdipCreateFromHDC`
- `GdipLoadImageFromFile`
- `GdipGetImageWidth/Height`
- `GdipDrawImageRectI`
- `GdipDeleteGraphics`
- `GdipDisposeImage`

Prevents the 64-bit `OverflowError: int too long to convert` after a print job.

## Status

- GDI+ page rendering validated through Microsoft Print to PDF
- job 16 was created on the Kyocera, but no new physical sheet was requested
- 365 tests
