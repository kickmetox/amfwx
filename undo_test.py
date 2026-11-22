from amfwx import DesignerDocument
d=DesignerDocument(); d.add('button','A'); d.move(0,50,60); print(d.items[0].x); d.undo(); print(d.items[0].x); d.redo(); print(d.items[0].x)
