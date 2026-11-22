import sys, ctypes
from pathlib import Path
sys.path.insert(0, r"D:\AI_Temp\AMFWX")
from amfwx import Window, Button
marker = Path(r"D:\AI_Temp\AMFWX\nvda_action_marker.txt")
marker.unlink(missing_ok=True)
w = Window("AMFWX Action Test", 420, 260)
button = Button("Aktion", on_click=lambda: marker.write_text("clicked"))
w.root.add(button); w._layout_root(); w._sync_a11y()
u = ctypes.windll.user32
u.SetForegroundWindow(ctypes.c_void_p(w.hwnd))
handle = w._a11y_windows[id(button)]
u.SetFocus(ctypes.c_void_p(handle))
Path(r"D:\AI_Temp\AMFWX\nvda_action_hwnd.txt").write_text(str(handle))
w.run()
