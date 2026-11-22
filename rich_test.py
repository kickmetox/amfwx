import sys, tempfile, os
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.clipboard import *
set_html("<b>Hallo</b>","Hallo"); print("html",get_html(),"text",get_text())
with tempfile.NamedTemporaryFile(delete=False) as f: p=f.name
set_files([p]); print("files",get_files()); os.unlink(p)
