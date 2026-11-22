import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, TextEdit
from amfwx.uia_provider import UiaProvider
from amfwx.uia_text import UIA_TextPatternId
w=Window("UIA Text",400,300); edit=TextEdit("hello"); w.root.children.clear(); w.root.add(edit)
p=UiaProvider(w); child=p.root.children[0]; print("text?",hasattr(child,"text_iface")); pattern=ctypes.c_void_p(); child._pattern(child.simple,UIA_TextPatternId,ctypes.pointer(pattern)); print("pattern",pattern.value)
tp=child.text_provider; rng=ctypes.c_void_p(); print("doc",tp._document(tp.simple,ctypes.pointer(rng))); print("range",rng.value)
# find range object
robj=[x for x in child.ranges if x.simple.value==rng.value][0]; out=ctypes.c_void_p(); print("gettext",robj._get_text(robj.simple,100,ctypes.pointer(out))); print(ctypes.wstring_at(out.value))
w.close(); w.process_events(30)
