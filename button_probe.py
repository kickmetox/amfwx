import ctypes,sys
from pathlib import Path
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window
u=ctypes.windll.user32
u.CreateWindowExW.restype=ctypes.c_void_p
w=Window("NativeButton",400,300)
style=u.GetWindowLongPtrW(ctypes.c_void_p(w.hwnd),-20)
u.SetWindowLongPtrW(ctypes.c_void_p(w.hwnd),-20,style|0x00010000)
child=u.CreateWindowExW(0,"BUTTON","Aktion",0x40000000|0x10000000,0,0,8,8,ctypes.c_void_p(w.hwnd),None,None,None)
Path(r"D:\AI_Temp\AMFWX\button_hwnd.txt").write_text(str(w.hwnd))
w.run()
