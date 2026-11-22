import sys
sys.path.insert(0,'tools')
import twain32_helper as h
lib=h.load(); import ctypes
app=h.app_identity(); user32=ctypes.WinDLL('user32'); user32.GetDesktopWindow.restype=ctypes.c_void_p; parent=ctypes.c_void_p(user32.GetDesktopWindow())
print('open',lib.DSM_Entry(ctypes.byref(app),None,1,4,h.MSG_OPENDSM,ctypes.byref(parent)))
ident=h.TW_IDENTITY(); print('first',lib.DSM_Entry(ctypes.byref(app),None,1,3,h.MSG_GETFIRST,ctypes.byref(ident)), 'id', ident.Id, 'name', h.text(ident.ProductName))
print('close',lib.DSM_Entry(ctypes.byref(app),None,1,4,h.MSG_CLOSEDSM,None))
