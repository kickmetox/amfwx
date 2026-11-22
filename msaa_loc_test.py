import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,read_location
w=Window("x",300,200); b=Button("Aktion"); w.root.add(b); w._layout_root(); print(read_location(w._a11y_windows[id(b)])); w.close(); w.process_events(40)
