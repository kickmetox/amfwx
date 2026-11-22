import ctypes, time
from pathlib import Path
u=ctypes.windll.user32; u.CreateWindowExW.restype=ctypes.c_void_p
h=u.CreateWindowExW(0,"#32770","UIA Dialog Host",0x00CF0000,100,100,400,200,None,None,None,None)
b=u.CreateWindowExW(0,"BUTTON","Aktion",0x50010000,20,20,120,32,ctypes.c_void_p(h),ctypes.c_void_p(1001),None,None)
print(h,b,u.IsWindow(ctypes.c_void_p(h)),u.IsWindow(ctypes.c_void_p(b)))
u.ShowWindow(ctypes.c_void_p(h),5); u.UpdateWindow(ctypes.c_void_p(h)); u.SetForegroundWindow(ctypes.c_void_p(h))
Path(r"D:\AI_Temp\AMFWX\dialog_host_hwnd.txt").write_text(f"{h}\n{b}")
# message pump
msg=ctypes.wintypes.MSG()
end=time.time()+8
while time.time()<end:
 while u.PeekMessageW(ctypes.byref(msg),None,0,0,1):
  u.TranslateMessage(ctypes.byref(msg)); u.DispatchMessageW(ctypes.byref(msg))
 time.sleep(0.01)
