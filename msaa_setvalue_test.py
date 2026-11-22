import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,LineEdit,set_accessible_value
w=Window("x",300,200); e=LineEdit("alt"); w.root.add(e); w._layout_root(); h=w._a11y_windows[id(e)]; print(set_accessible_value(h,"neu")); w.process_events(200); print(e.text()); w.close(); w.process_events(40)
