# RichText

AMFWX has a small HTML-subset rich text widget.

```python
from amfwx import RichText

view = RichText("<h1>Titel</h1><p>Hallo <b>Welt</b> "
                "<a href='#x'>Link</a></p>")
```

Supported tags:

- `p`, `div`, `br`
- `h1`, `h2`, `h3`
- `b`, `strong`
- `i`, `em`
- `u`
- `a`
- `li`

Rendering uses the built-in text renderer. Bold is simulated by a second
draw; links use the accent color.

## Limits

- no CSS
- no images
- no tables
- no nested lists
- no full HTML parser
- no link click handling yet
