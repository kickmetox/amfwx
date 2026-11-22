import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button
from amfwx.uia_provider import UiaProvider, IID_ROOT, IID_FRAGMENT
w=Window("x",300,200); w.root.add(Button("b")); w.enable_uia(); p=UiaProvider(w)
for iid in (IID_ROOT,IID_FRAGMENT):
 out=ctypes.c_void_p(); r=p.root._query(p.root.simple,ctypes.byref(iid),ctypes.pointer(out)); print(iid,r,out.value)
print("simple",p.root.simple.value,"root",p.root.root_iface.value,"frag",p.root.fragment.value)
print("children",len(p.root.children)); w.close()
