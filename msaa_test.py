import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button
from amfwx.msaa import read_accessible
w=Window("x",300,200); w.root.add(Button("Aktion")); w._layout_root(); h=list(w._a11y_windows.values())[0]; print(read_accessible(h)); w.close(); w.process_events(40)
