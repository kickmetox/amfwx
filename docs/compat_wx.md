# wxWidgets compatibility

Small AMFWX-native wxWidgets interpretation.

```python
from amfwx.compat import wx

app = wx.App()
frame = wx.Frame(None, title="Demo", size=(640, 400))
panel = wx.Panel(frame)
sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(wx.StaticText(panel, label="Hallo"))
sizer.Add(wx.Button(panel, label="OK"))
panel.SetSizer(sizer)
frame.Show()
app.MainLoop()
```

## Included

- `App`
- `Frame`
- `Panel`
- `BoxSizer`
- `StaticText`
- `Button`
- `TextCtrl`
- `CheckBox`
- `Gauge`
- `Choice`
- `Menu`, `MenuBar`, `StatusBar`
- `Bind`
- constants: `VERTICAL`, `HORIZONTAL`, `ALL`, `EXPAND`, `EVT_BUTTON`

## Limits

- no native wx controls
- no grid sizer
- no dialogs yet
- no `wx.EVT_TEXT` live binding
- simple box sizers only
