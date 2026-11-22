import ctypes, time
u=ctypes.windll.user32
# Send space to focused window
u.keybd_event(0x20,0,0,0)
u.keybd_event(0x20,0,2,0)
time.sleep(1)
