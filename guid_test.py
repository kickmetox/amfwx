import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.uia_provider import IID_ROOT,IID_FRAGMENT,_guid
print("root",str(IID_ROOT),"frag",str(IID_FRAGMENT))
print("parsed",_guid(ctypes.byref(IID_ROOT)))
