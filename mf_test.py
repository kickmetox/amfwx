import ctypes,sys
d=ctypes.WinDLL(r"D:\AI_Temp\AMFWX\amfwx\bin\mfdecode.dll")
d.mf_probe.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int)]
w=ctypes.c_int();h=ctypes.c_int();n=ctypes.c_int(); print("probe",d.mf_probe(r"C:\Users\Lenovo\Desktop\Demo2.mp4",ctypes.byref(w),ctypes.byref(h),ctypes.byref(n)),w.value,h.value,n.value)
buf=(ctypes.c_ubyte*(w.value*h.value*4))(); st=ctypes.c_int(); print("decode",d.mf_decode_frame(r"C:\Users\Lenovo\Desktop\Demo2.mp4",0,buf,len(buf),ctypes.byref(w),ctypes.byref(h),ctypes.byref(st)),st.value)
