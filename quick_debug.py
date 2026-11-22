import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.quick import QuickView,State,Text
s=State("A"); w=QuickView("Quick",lambda v:[Text(v)],state=s); print([(type(c).__name__,c.text) for c in w.root.children]); s.set("B"); print([(type(c).__name__,c.text) for c in w.root.children]); w.dispose(); w.process_events(40)
