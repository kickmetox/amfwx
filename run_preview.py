import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window, BoxLayout, Label, LineEdit, CheckBox, Slider, ComboBox, Button, MenuBar, TableView
w=Window("AMFWX",700,500)
layout=BoxLayout(spacing=10,padding=18)
w.layout=layout; w.root.children.clear()
menubar=MenuBar(); m=menubar.add_menu("Datei"); m.add("Öffnen"); m.add("Beenden")
table=TableView(["Name","Wert"],[["Alpha","1"],["Beta","2"],["Gamma","3"]])
items=[menubar, Label("AMFWX",scale=3), table, LineEdit("Text"), ComboBox(["Deutsch","English","العربية"]), CheckBox("Aktiv",True), Button("Weiter",variant="primary")]
for x in items: w.root.add(x); layout.add(x, 1 if x is table else 0)
w.set_focus(items[3]); w._layout_root(); w.invalidate(); w.process_events(100); w.render_to_bmp("preview4.bmp"); print("ok"); w.close(); w.process_events(80)
