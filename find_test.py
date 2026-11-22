import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, TextEdit
from amfwx.dialog import FindReplaceDialog
w=Window("x",400,300); e=TextEdit("eins zwei eins"); w.root.add(e); w.editor=e
d=FindReplaceDialog(w); d.find_input.set_text("eins"); d.find_next(); print(e.selected_text()); d.replace_input.set_text("drei"); d.replace_all(); print(e.text()); w.close()
