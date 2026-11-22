import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button
from amfwx.uia_provider import UiaProvider,UIA_NamePropertyId,UIA_ControlTypePropertyId,VARIANT
w=Window("native",300,200); w.root.add(Button("b")); p=UiaProvider(w)
for prop in (UIA_NamePropertyId,UIA_ControlTypePropertyId):
 v=VARIANT(); r=p.root._property(p.root.simple,prop,ctypes.pointer(v)); print(prop,r,v.vt,v.value,ctypes.wstring_at(v.value) if v.vt==8 and v.value else None)
w.close()
