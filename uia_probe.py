"""Helper window for UIA client probes."""

import ctypes
import sys
import time
from pathlib import Path

sys.path.insert(0, r"D:\AI_Temp\AMFWX")

from amfwx import Button, Label, TextEdit, Window


window = Window("AMFWX UIA Probe", 420, 260)
label = Label("Probe")
button = Button("Aktion")
edit = TextEdit("Text")
window.root.add(label)
window.root.add(button)
window.root.add(edit)
window.enable_uia()
window.enable_msaa()
window.title = "CUSTOM_PROVIDER_NAME"
Path("D:/AI_Temp/AMFWX/uia_hwnd.txt").write_text(str(window.hwnd))
window.run()
