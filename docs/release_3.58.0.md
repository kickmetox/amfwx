# AMFWX 3.58.0

AMFWX 3.58 adds eSCL duplex and scan regions.

## New

- `duplex` parameter
- `region=(x, y, width, height)`
- 279 tests

## Usage

```python
scanner.scan("scan.jpg", duplex=True,
             region=(0, 0, 2480, 3508))
scanner.scan_pages("out", duplex=True)
```
