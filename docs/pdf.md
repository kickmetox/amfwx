# PDF export

AMFWX can export any canvas or window as a PDF page.

```python
canvas.save_pdf("page.pdf")
window.render_to_pdf("window.pdf")
```

The PDF embeds the canvas as a lossless RGB image with Flate compression.
It is a single-page PDF for printing, previews and export.

## Limits

- one page per canvas
- no vector text (currently rasterized)
- no PDF printer dialog
- no multipage document model
- no PDF/A

## Use cases

- print preview
- export screenshots
- reports
- attaching UI state to a bug report
