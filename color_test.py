import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, ColorDialog, Color
w=Window("x",300,200); d=ColorDialog(w,Color(1,2,3)); d.fields["R"].set_text("255"); d.fields["G"].set_text("10"); d.fields["B"].set_text("20"); d._update(); print(d.color); d.close(); w.close()
