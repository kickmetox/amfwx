import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
import amfwx.clipboard as c
print(c.set_html("<b>Hallo</b>", "Hallo"))
print("html",repr(c.get_html()),"text",repr(c.get_text()))
