import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button
from amfwx.uia_native import notify_focus
w=Window("x",300,200); b=Button("A"); w.root.add(b); w._layout_root(); w._sync_a11y(); h=w._a11y_windows[id(b)]; print(notify_focus(h)); w.close(); w.process_events(40)
