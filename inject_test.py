import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
import amfwx.uia_native as un
def fail(*a,**k): raise OSError("missing dll")
un._library=fail
from amfwx import Window,Button
w=Window("x",300,200); b=Button("A"); w.root.add(b); w._layout_root(); w._sync_a11y(); print("ok",w._a11y_windows); w.close(); w.process_events(40)
