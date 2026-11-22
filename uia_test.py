import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, Label, Button
from amfwx.uia_provider import UiaProvider, VARIANT, UIA_NamePropertyId, UIA_ControlTypePropertyId
w=Window("UIA Test",400,300); l=Label("Name"); b=Button("OK"); w.root.children.clear(); w.root.add(l); w.root.add(b)
p=UiaProvider(w); print("root",p.root.simple.value, "children",len(p.root.children)); v=VARIANT(); p.root._property(p.root.simple, UIA_NamePropertyId, __import__("ctypes").pointer(v)); print("name vt",v.vt); p.root._property(p.root.simple,UIA_ControlTypePropertyId,__import__("ctypes").pointer(v)); print("ct",v.value); w.close(); w.process_events(30)
