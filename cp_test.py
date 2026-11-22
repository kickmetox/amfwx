import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,Label,TextEdit
w=Window("x",300,200); w.root.add(Label("L")); w.root.add(Button("B")); w.root.add(TextEdit("E")); w._layout_root(); print(len(w._a11y_windows)); w.close()
