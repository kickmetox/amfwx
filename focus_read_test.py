import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,select_accessible,read_focus
w=Window("x",300,200); b=Button("Aktion"); w.root.add(b); w._layout_root(); h=w._a11y_windows[id(b)]; print(read_focus(h)); print(select_accessible(h)); w.process_events(100); print(read_focus(h)); w.close(); w.process_events(40)
