import ctypes,sys
sys.path.insert(0,'tools'); import twain32_helper as h
lib=h.load(); user32=ctypes.WinDLL('user32'); user32.GetDesktopWindow.restype=ctypes.c_void_p; parent=ctypes.c_void_p(user32.GetDesktopWindow()); app=h.app_identity()
lib.DSM_Entry(ctypes.byref(app),None,1,4,h.MSG_OPENDSM,ctypes.byref(parent))
for i in range(0,6):
 ident=h.TW_IDENTITY(); ident.Id=i
 print(i,lib.DSM_Entry(ctypes.byref(app),ctypes.byref(ident),1,3,h.MSG_OPENDS,None))
lib.DSM_Entry(ctypes.byref(app),None,1,4,h.MSG_CLOSEDSM,None)
