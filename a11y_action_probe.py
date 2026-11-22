import sys
from pathlib import Path
sys.path.insert(0, r"D:\AI_Temp\AMFWX")
from amfwx import Window, Button
window = Window("UIA Action", 420, 260)
marker = Path(r"D:\AI_Temp\AMFWX\uia_clicked.txt")
button = Button("Aktion", on_click=lambda: marker.write_text("clicked"))
window.root.add(button)
Path(r"D:\AI_Temp\AMFWX\uia_action_hwnd.txt").write_text(str(window.hwnd))
window.run()
