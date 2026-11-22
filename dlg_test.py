import ctypes, struct, time
from pathlib import Path
from ctypes import wintypes
u=ctypes.windll.user32; k=ctypes.windll.kernel32
u.CreateDialogIndirectParamW.restype=ctypes.c_void_p
u.CreateDialogIndirectParamW.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p]
DLGPROC=ctypes.WINFUNCTYPE(ctypes.c_ssize_t,ctypes.c_void_p,ctypes.c_uint,ctypes.c_size_t,ctypes.c_ssize_t)
def dlgproc(hwnd,msg,wparam,lparam):
    if msg==0x0110: return 1  # WM_INITDIALOG
    if msg==0x0111: return 1  # WM_COMMAND
    if msg==0x0010: u.EndDialog(ctypes.c_void_p(hwnd),0); return 1
    return 0
proc=DLGPROC(dlgproc)
# dialog template
buf=bytearray()
style=0x80C80080  # WS_POPUP|WS_CAPTION|WS_SYSMENU|DS_MODALFRAME
buf+=struct.pack('<IIHhhhh',style,0,1,0,0,260,140)
buf+=struct.pack('<HHH',0,0,0)  # menu, class, empty title
while len(buf)%4: buf+=b'\x00'
# item template
buf+=struct.pack('<IIhhhhH',0x50010000,0,20,20,120,32,1001)
buf+=("BUTTON\x00").encode('utf-16le')
buf+=("Aktion\x00").encode('utf-16le')
buf+=struct.pack('<H',0)
while len(buf)%4: buf+=b'\x00'
mem=ctypes.create_string_buffer(bytes(buf),len(buf))
inst=k.GetModuleHandleW(None)
h=u.CreateDialogIndirectParamW(ctypes.c_void_p(inst),ctypes.cast(mem,ctypes.c_void_p),None,ctypes.cast(proc,ctypes.c_void_p),0)
print("dialog",h,flush=True)
if h:
    u.ShowWindow(ctypes.c_void_p(h),5); u.UpdateWindow(ctypes.c_void_p(h)); u.SetForegroundWindow(ctypes.c_void_p(h))
    # find button
    btn=u.GetDlgItem(ctypes.c_void_p(h),1001)
    print('btn',btn,'visible',u.IsWindowVisible(ctypes.c_void_p(h)),flush=True)
    Path(r"D:\AI_Temp\AMFWX\dlg_hwnd.txt").write_text(f"{h}\n{btn}")
    end=time.time()+10
    msg=wintypes.MSG()
    while time.time()<end:
        while u.PeekMessageW(ctypes.byref(msg),None,0,0,1):
            if msg.message==0x0012: break
            u.TranslateMessage(ctypes.byref(msg)); u.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.01)
