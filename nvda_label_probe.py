import sys, ctypes
from pathlib import Path
sys.path.insert(0, r"D:\AI_Temp\AMFWX")
from amfwx import Window, Label, LineEdit, Button
w = Window("AMFWX Label Test", 520, 320)
label = Label("Name", label_for=None)
edit = LineEdit("Text")
label.label_for = edit
w.root.add(label); w.root.add(edit); w.root.add(Button("OK"))
label.arrange(__import__('amfwx').Rect(20,20,200,24)); edit.arrange(__import__('amfwx').Rect(20,60,240,32))
w._layout_root(); w._sync_a11y()
u = ctypes.windll.user32
u.SetForegroundWindow(ctypes.c_void_p(w.hwnd))
u.SetFocus(ctypes.c_void_p(w._a11y_windows[id(edit)]))
Path(r"D:\AI_Temp\AMFWX\nvda_label_hwnd.txt").write_text(str(w.hwnd))
w.run()
