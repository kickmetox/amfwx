import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.mfvideo import _library
lib=_library(); w=ctypes.c_int();h=ctypes.c_int();st=ctypes.c_int(); size=4096*2160*3//2; buf=(ctypes.c_ubyte*size)(); n=lib.mf_decode_frame(r"C:\Users\Lenovo\Desktop\Demo2.mp4",100,buf,size,ctypes.byref(w),ctypes.byref(h),ctypes.byref(st)); print(n,w.value,h.value,st.value, list(buf[:20]))
