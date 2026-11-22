import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, TableView
from amfwx.uia_provider import UiaProvider
w=Window("x",300,200); t=TableView(["A"],[["x"]]); t.selected=0; w.root.children.clear(); w.root.add(t)
p=UiaProvider(w); c=p.root.children[0]; print(type(c.widget).__name__,hasattr(c,"selection"),c._cells.keys()); w.close()
