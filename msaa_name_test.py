import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,LineEdit,set_accessible_name,read_accessible
w=Window("x",300,200); e=LineEdit("Text"); w.root.add(e); w._layout_root(); h=w._a11y_windows[id(e)]; print(set_accessible_name(h,"Beschriftung")); print(read_accessible(h)); w.close(); w.process_events(40)
