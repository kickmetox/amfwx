# AMFWX 4.7.0

Correct GDI+ page handling for PDF printing.

## Fix

- `StartPage` / `EndPage` around every GDI+ page
- GDI+ page unit explicitly set to pixels
- PDF rendering via PyMuPDF
- 150 dpi, capped at 1500x2100
- 365 tests

## Validation

Rendered a test page through `Microsoft Print to PDF`; the output PDF contains
the drawn text. The earlier blank pages came from drawing before `StartPage`.

## Note

The older queued test jobs were canceled. A new physical test page has not been
sent after this fix.
