import tempfile, zipfile, os
from amfwx import ResourcePack, CrashLogger
with tempfile.TemporaryDirectory() as d:
 p=os.path.join(d,'r.zip')
 with zipfile.ZipFile(p,'w') as z: z.writestr('theme.json','{"name":"x"}')
 with ResourcePack(p) as r: print(r.json('theme.json'))
 c=CrashLogger(os.path.join(d,'crash.log'))
 try: 1/0
 except Exception as e: c.log(e)
 print(os.path.getsize(os.path.join(d,'crash.log')))
