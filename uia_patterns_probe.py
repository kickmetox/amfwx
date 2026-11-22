import sys, ctypes
from pathlib import Path
sys.path.insert(0, r"D:\AI_Temp\AMFWX")
from amfwx import Window, Label, LineEdit, CheckBox
w = Window("UIA Patterns", 520, 320)
edit = LineEdit("alt")
label = Label("Name", label_for=edit)
check = CheckBox("An")
w.root.add(label); w.root.add(edit); w.root.add(check)
label.arrange(__import__('amfwx').Rect(20,20,200,24)); edit.arrange(__import__('amfwx').Rect(20,60,240,32)); check.arrange(__import__('amfwx').Rect(20,110,120,28))
w._layout_root(); w._sync_a11y()
u = ctypes.windll.user32
u.SetForegroundWindow(ctypes.c_void_p(w.hwnd))
Path(r"D:\AI_Temp\AMFWX\uia_patterns_handles.txt").write_text(
    f"{w.hwnd}\n{w._a11y_windows[id(edit)]}\n{w._a11y_windows[id(check)]}")
w.run()
