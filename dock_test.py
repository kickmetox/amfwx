import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import DockManager,Label,Panel,Rect
m=DockManager(Label("C")); m.add_pane("L",Label("L"),"left",100); m.add_pane("B",Label("B"),"bottom",80); m.arrange(Rect(0,0,400,300)); print(m.central.rect, m.panes[0].widget.rect, m.panes[1].widget.rect)
