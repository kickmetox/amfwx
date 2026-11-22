import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,CheckBox,LineEdit
from amfwx.msaa import read_accessible
w=Window("x",300,200); b=Button("Aktion"); c=CheckBox("An"); e=LineEdit("Text"); w.root.add(b); w.root.add(c); w.root.add(e); w._layout_root()
for wid in (b,c,e):
 h=w._a11y_windows[id(wid)]; print(type(wid).__name__,read_accessible(h))
w.close(); w.process_events(40)
