import sys, ctypes
from pathlib import Path
sys.path.insert(0, r"D:\AI_Temp\AMFWX")
from amfwx import Window, Button, LineEdit, Rect
w = Window("AMFWX Formular", 520, 320)
first = Button("Eins")
second = Button("Zwei")
edit = LineEdit("Text")
label = __import__("amfwx").Label("Name", label_for=edit)
w.root.add(label); w.root.add(first); w.root.add(second); w.root.add(edit)
label.arrange(Rect(20, 20, 200, 24)); first.arrange(Rect(20, 60, 180, 32)); second.arrange(Rect(20, 104, 180, 32)); edit.arrange(Rect(20, 148, 240, 32))
w._layout_root(); w._sync_a11y()
u = ctypes.windll.user32
u.SetForegroundWindow(ctypes.c_void_p(w.hwnd))
h1 = w._a11y_windows[id(first)]; h2 = w._a11y_windows[id(second)]; he = w._a11y_windows[id(edit)]
u.SetFocus(ctypes.c_void_p(h1))
Path(r"D:\AI_Temp\AMFWX\nvda_tab_handles.txt").write_text(f"{w.hwnd}\n{h1}\n{h2}\n{he}")
w.run()
