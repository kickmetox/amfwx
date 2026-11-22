import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,Label
w=Window("x",400,300); w.root.add(Label("Hallo")); w.root.add(Button("OK")); w._layout_root(); print("a11y",len(w._a11y_windows),w._a11y_windows); w.close()
