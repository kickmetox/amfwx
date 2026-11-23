# AMFWX 4.8.0

Use GDI-DIB for Windows printing.

## Fix

- replace GDI+ drawing with GDI `StretchDIBits`
- `StartPage` / `EndPage` per page
- full-page scaling
- test page renders in `Microsoft Print to PDF`

## New queue

The existing WSD queue produced blank pages and hung jobs. Added:

```text
Printer: AMFWX Kyocera
Port:    AMFWX_192.168.178.93
Address:192.168.178.93:9100
Driver: Kyocera ECOSYS M5521cdn XPS
```

A test job was sent to this queue without hanging.

365 tests.
