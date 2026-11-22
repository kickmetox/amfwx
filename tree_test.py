import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Label,Button,LineEdit
w=Window("x",400,300); e=LineEdit("Text"); w.root.add(Label("Name",label_for=e)); w.root.add(e); w.root.add(Button("OK")); w._layout_root(); t=w.accessibility_tree(); print([(n.role,n.name,n.value) for n in t.walk()]); w.close(); w.process_events(40)
