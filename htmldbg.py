import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
import amfwx.clipboard as c
print("fmt",c.CF_HTML)
print("set",c.set_html("<b>Hallo</b>","Hallo"))
u=c.user32; k=c.kernel32
u.OpenClipboard(None); h=u.GetClipboardData(c.CF_HTML); print("handle",h); p=k.GlobalLock(h); print("ptr",p); print(ctypes.string_at(p)[:200] if p else None); u.CloseClipboard()
print("get",repr(c.get_html()))
