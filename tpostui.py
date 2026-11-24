from amfwx import ScanWindow, ScannerWindow
w=ScanWindow(); print(w.deskew.checked, w.crop.checked); w.close(); s=ScannerWindow(); print(s.deskew.checked); s.close()
