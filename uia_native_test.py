import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,LineEdit
from amfwx.uia_native import attach
w=Window("UIA",400,300); b=Button("Aktion"); e=LineEdit("Text"); w.root.add(b); w.root.add(e); w._layout_root(); w._sync_a11y(); print(w._a11y_windows); w.close(); w.process_events(40)
