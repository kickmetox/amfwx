import ctypes,sys
from pathlib import Path
u=ctypes.windll.user32
u.CreateWindowExW.restype=ctypes.c_void_p
h=u.CreateWindowExW(0,"BUTTON","Aktion",0x00CF0000,100,100,160,40,None,None,None,None)
Path(r"D:\AI_Temp\AMFWX\topbtn_hwnd.txt").write_text(str(h))
ctypes.windll.user32.ShowWindow(ctypes.c_void_p(h),5)
ctypes.windll.user32.UpdateWindow(ctypes.c_void_p(h))
import time
time.sleep(10)
