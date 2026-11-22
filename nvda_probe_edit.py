import sys, ctypes
from pathlib import Path
sys.path.insert(0, r"D:\AI_Temp\AMFWX")
from amfwx import Window, Label, Button, LineEdit
w = Window("AMFWX Screenreader Test", 520, 320)
label = Label("Beschriftung"); button = Button("Aktion"); edit = LineEdit("Textfeld")
w.root.add(label); w.root.add(button); w.root.add(edit)
w._layout_root(); w._sync_a11y()
u = ctypes.windll.user32
u.SetForegroundWindow(ctypes.c_void_p(w.hwnd))
handles = {type(x).__name__: h for h, x in w._a11y_by_handle.items()}
u.SetFocus(ctypes.c_void_p(handles.get("LineEdit", w.hwnd)))
w.run()
