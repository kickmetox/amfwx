import sys,tempfile,os
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Settings
p=tempfile.mktemp(suffix=".json"); s=Settings(p); s.set("a",1); s.add_recent("x"); print(Settings(p).get("a"), Settings(p).recent()); os.unlink(p)
