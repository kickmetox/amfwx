import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button
w=Window("Tab",400,300); b1=Button("Eins"); b2=Button("Zwei"); w.root.add(b1); w.root.add(b2); w._layout_root(); w._sync_a11y(); u=ctypes.windll.user32; h1=w._a11y_windows[id(b1)]; h2=w._a11y_windows[id(b2)]; print(h1,h2); u.SetForegroundWindow(ctypes.c_void_p(w.hwnd)); w.process_events(50); u.SetFocus(ctypes.c_void_p(h1)); print("focus1",u.GetFocus()); u.SendMessageW(ctypes.c_void_p(w.hwnd),0x0028,0,0); w.process_events(60); print("after",u.GetFocus()); w.close(); w.process_events(40)
