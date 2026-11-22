import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, FontDialog
w=Window("x",400,300); d=FontDialog(w); print(len(d.fonts), d.font.size, d.preview.text); d.size_input.set_text("24"); d._update(); print(d.font.size); d.close(); w.close()
