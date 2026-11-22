import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import DockManager,Label,Rect
m=DockManager(Label("C")); p=m.add_pane("L",Label("L"),"left",100); m.arrange(Rect(0,0,400,300)); w=m.float_pane(p); print(len(m.panes)); w.close(); w.process_events(100); print(len(m.panes))
