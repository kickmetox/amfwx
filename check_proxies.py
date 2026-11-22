import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Label,LineEdit,CheckBox
w=Window("UIA Patterns",520,320); e=LineEdit("alt"); l=Label("Name",label_for=e); c=CheckBox("An"); w.root.add(l); w.root.add(e); w.root.add(c); w._layout_root(); w._sync_a11y(); print("proxies",len(w._a11y_windows),"uia",w._uia_native)
for wid in (l,e,c):
 h=w._a11y_windows.get(id(wid)); print(type(wid).__name__,h, "rect",wid.rect)
w.close(); w.process_events(40)
