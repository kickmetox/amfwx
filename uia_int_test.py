import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button
w=Window("UIA",400,300); b=Button("Aktion"); w.root.add(b); w._layout_root(); w._sync_a11y(); print(w._uia_native); w.close(); w.process_events(40)
