import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Label
from amfwx.widgets import Menu
w=Window("x",400,300); l=Label("x"); m=Menu("m"); m.add("a",lambda:None); l.context_menu=m; w.root.children.clear(); w.root.add(l); w._layout_root(); print("rect",l.rect,"at",w._widget_at(l.rect.x+4,l.rect.y+4)); w._context_menu(l.rect.x+4,l.rect.y+4); print("overlay",w.overlay); w.close()
