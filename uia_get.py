import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, Label
w=Window("UIA",300,200); w.root.add(Label("x")); w.enable_uia(); print("result",w._uia_getobject()); w.close(); w.process_events(20)
