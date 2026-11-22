# AMFWX Designer

A small visual form designer is included.

```python
from amfwx import DesignerWindow
DesignerWindow().run()
```

## Features

- palette: label, button, line_edit, text_edit, checkbox, slider, combo, progress
- click an item to select it
- drag to move
- JSON save/load
- Python code generation
- grid canvas

## Document API

```python
from amfwx import DesignerDocument

document = DesignerDocument("Formular")
document.add("label", "Name", 20, 20, 160, 24)
document.add("button", "OK", 20, 60, 120, 32)
document.save("form.json")
code = document.generate_code()
```

## Limits

- absolute positions only
- resize via the bottom-right handle
- undo/redo with Ctrl+Z / Ctrl+Y
- no property editor for every attribute
- no resource/icon picker
- code generation uses `Rect` and absolute layout

## Status

The designer is usable for simple forms. It is not yet an AMFW Studio
equivalent.
