# AMFWX 4.7.1

Make the PDF print test optional.

## Fix

- skip `test_pdf_print` when PyMuPDF is absent
- keeps CI green without an optional renderer
- 365 tests

## Printing status

- GDI+ page frame fixed (`StartPage`/`EndPage`)
- GDI+ page unit set to pixels
- validated through `Microsoft Print to PDF`
- physical Kyocera print was **not** re-tested after the fix
- older blank test jobs were canceled
