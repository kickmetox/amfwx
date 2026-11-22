import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
import amfwx.clipboard as c
u=c.user32;k=c.kernel32
data=b"test\0"; print("open",u.OpenClipboard(None)); print("empty",u.EmptyClipboard()); h=k.GlobalAlloc(c.GMEM_MOVEABLE,len(data)); print("h",h); p=k.GlobalLock(h); print("p",p); ctypes.memmove(p,data,len(data)); k.GlobalUnlock(h); r=u.SetClipboardData(c.CF_HTML,h); print("set",r,"err",ctypes.get_last_error()); print("get",u.GetClipboardData(c.CF_HTML)); u.CloseClipboard()
