import ctypes,sys
from pathlib import Path
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window
u=ctypes.windll.user32
u.CreateWindowExW.restype=ctypes.c_void_p
w=Window("NativeStatic",400,300)
child=u.CreateWindowExW(0,"STATIC","A11Y-LABEL",0x40000000|0x10000000,0,0,1,1,ctypes.c_void_p(w.hwnd),None,None,None)
print("child",child,flush=True)
Path(r"D:\AI_Temp\AMFWX\static_hwnd.txt").write_text(str(w.hwnd))
w.run()
