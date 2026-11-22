import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
import amfwx.clipboard as c
print("fmt",c.CF_HTML)
print("set",c.set_html("<b>Hallo</b>"))
u=c.user32
u.OpenClipboard(None); print("formats?")
# enumerate
fmt=0
while True:
 fmt=u.EnumClipboardFormats(fmt)
 if not fmt: break
 print("fmt",fmt)
u.CloseClipboard()
print("get",repr(c.get_html()))
