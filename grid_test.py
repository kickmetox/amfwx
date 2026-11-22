import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,TableView
from amfwx.uia_provider import UiaProvider,UIA_GridPatternId
w=Window("x",400,300); t=TableView(["A","B"],[["1","2"],["3","4"]]); w.root.children.clear(); w.root.add(t)
p=UiaProvider(w); node=p.root.children[0]; print("rows",len(node.children),"cells",len(node.children[0].children))
pat=ctypes.c_void_p(); node._pattern(node.simple,UIA_GridPatternId,ctypes.pointer(pat)); print("pat",pat.value)
r=ctypes.c_int(); c=ctypes.c_int(); node._grid_rows(node.simple,ctypes.pointer(r)); node._grid_columns(node.simple,ctypes.pointer(c)); print(r.value,c.value)
cell=ctypes.c_void_p(); node._grid_item(node.simple,1,1,ctypes.pointer(cell)); print("cell",cell.value)
w.close()
