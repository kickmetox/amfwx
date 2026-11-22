# Tkinter compatibility

AMFWX provides a small Tkinter-style adapter.

```python
from amfwx.compat import tkinter as tk

root = tk.Tk()
root.title("Demo")
value = tk.StringVar("Hallo")
tk.Label(root, text="Name").pack()
tk.Entry(root, textvariable=value).pack()
tk.Button(root, text="OK", command=lambda: print(value.get())).pack()
root.mainloop()
```

## Included

- `Tk`
- `Frame`
- `Label`
- `Button`
- `Entry`
- `Checkbutton`
- `Canvas`
- `ttk.Notebook`
- `ttk.Treeview`
- `ttk.Progressbar`
- `ttk.Combobox`
- `Menu`
- `StringVar`, `IntVar`, `DoubleVar`, `BooleanVar`
- `pack`, `grid`, `place`
- `messagebox`

## Not Tcl/Tk

This is an AMFWX-native interpretation:

- no Tcl interpreter
- no Tk DLLs
- no `ttk` themes
- no canvas item model
- no full event loop API (`after` runs immediately)

## Limits

- pack layouts are simple vertical/horizontal
- grid uses fixed cell sizes
- no real menu bar
- no image support yet
