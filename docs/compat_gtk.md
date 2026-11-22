# GTK compatibility

Small AMFWX-native GTK interpretation.

```python
from amfwx.compat import gtk as Gtk

app = Gtk.Application()
window = Gtk.ApplicationWindow(application=app, title="Demo")
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
window.set_child(box)
box.append(Gtk.Label(label="Hallo"))
button = Gtk.Button(label="OK")
button.connect("clicked", lambda _button: print("OK"))
box.append(button)
window.present()
app.run([])
```

## Included

- `Application`
- `ApplicationWindow`
- `Box`
- `Grid`
- `Label`
- `Button`
- `Entry`
- `CheckButton`
- `Switch`
- `Scale`
- `ProgressBar`
- `Separator`
- `HeaderBar`
- `Orientation`

## Limits

- no GTK/libgtk
- no CSS
- no GTK templates
- no list/tree models
- no native dialogs
- box/grid layouts only
