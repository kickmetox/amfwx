import sys, ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFW"); sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfw import Application, Window as AWindow, Label
from amfwx import Window as XWindow
from amfwx.amfw_bridge import AmfwxWindowHost
app=Application(theme="dark")
aw=AWindow("AMFW child",300,200); aw.set_central_widget(Label("embedded")); aw.show(); app.process_events(40)
xw=XWindow("AMFWX host",600,400); host=AmfwxWindowHost(aw).attach(xw); app.process_events(60)
u=ctypes.WinDLL("user32"); u.GetParent.argtypes=[ctypes.c_void_p]; u.GetParent.restype=ctypes.c_void_p
print("parent", int(u.GetParent(aw.hwnd) or 0), "host", xw.hwnd); xw.close(); app.process_events(30)
