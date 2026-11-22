from amfwx import TableModel, SortFilterModel
m=TableModel(["A","B"],[["x",2],["y",1]]); f=SortFilterModel(m,0,""); print(f.row_count(),f.data(0,0)); m.append_row(["z",3]); print(f.row_count()); f.set_query("z"); print(f.row_count(),f.data(0,0))
