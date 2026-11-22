import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,Label,LineEdit,CheckBox
w=Window("x",400,300); b=Button("OK"); e=LineEdit("Text"); c=CheckBox("An"); w.root.add(Label("Name",label_for=e)); w.root.add(e); w.root.add(b); w.root.add(c); w._layout_root(); w.sync_accessibility(); print(w.accessibility_bridge().node(e)); w.close(); w.process_events(40)
