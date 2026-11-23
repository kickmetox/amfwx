# AMFWX 3.57.0

AMFWX 3.57 adds eSCL multi-page/ADF support.

## New

- `EsclScanner.scan_pages`
- repeated `NextDocument`
- stop on 204/404
- 278 tests

## Usage

```python
scanner.scan_pages("out", prefix="page", max_pages=50)
```
