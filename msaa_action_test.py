import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx import Window,Button,do_default_action
clicked=[]; w=Window("x",300,200); b=Button("Aktion",on_click=lambda: clicked.append(1)); w.root.add(b); w._layout_root(); h=list(w._a11y_windows.values())[0]; print(do_default_action(h)); w.process_events(200); print(clicked); w.close(); w.process_events(40)
