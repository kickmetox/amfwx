import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.quick import QuickView,State,Text
s=State("A"); w=QuickView("Quick",lambda v:[Text(v)]); print(w.root.children[0].text); s.set("B"); print(w.root.children[0].text); w.close(); w.process_events(40)
