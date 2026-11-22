import subprocess,sys
print(subprocess.run([r'D:\AI_Temp\AMFWX\vendor\python32\python.exe', r'D:\AI_Temp\AMFWX\amfwx\twain32_helper.py','--list'],capture_output=True,text=True).stdout)
