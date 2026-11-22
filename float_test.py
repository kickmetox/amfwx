import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import DockManager,Label,Rect
m=DockManager(Label("C")); pane=m.add_pane("L",Label("L"),"left",100); m.arrange(Rect(0,0,400,300)); w=m.float_pane(pane); print(len(m.panes),w.title); w.close()
