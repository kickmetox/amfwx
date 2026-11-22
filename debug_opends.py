import ctypes, sys
sys.path.insert(0,'tools'); import twain32_helper as h
lib=h.load(); user32=ctypes.WinDLL('user32'); user32.GetDesktopWindow.restype=ctypes.c_void_p; parent=ctypes.c_void_p(user32.GetDesktopWindow()); app=h.app_identity()
print('open',lib.DSM_Entry(ctypes.byref(app),None,1,4,h.MSG_OPENDSM,ctypes.byref(parent)))
ident=h.TW_IDENTITY(); rc=lib.DSM_Entry(ctypes.byref(app),None,1,3,h.MSG_GETFIRST,ctypes.byref(ident)); print('first',rc,ident.Id,h.text(ident.ProductName))
for mode in ('id','name'):
 i=h.TW_IDENTITY(); i.Id=ident.Id if mode=='id' else 0
 i.ProductName=ident.ProductName
 print(mode,'openDS',lib.DSM_Entry(ctypes.byref(app),ctypes.byref(i),1,3,h.MSG_OPENDS,None))
 if mode=='name': lib.DSM_Entry(None,ctypes.byref(i),1,3,h.MSG_CLOSEDS,None)
lib.DSM_Entry(ctypes.byref(app),None,1,4,h.MSG_CLOSEDSM,None)
