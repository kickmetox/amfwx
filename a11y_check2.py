import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Label,Button,TextEdit
w=Window("A11Y",400,300); w.root.add(Label("Label")); w.root.add(Button("Button")); w.root.add(TextEdit("Edit")); w._layout_root(); print(len(w._a11y_windows));
for h in w._a11y_windows.values():
 import ctypes
 b=ctypes.create_unicode_buffer(64); ctypes.windll.user32.GetWindowTextW(h,b,64); print(b.value)
w.close()
