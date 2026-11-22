Add-Type @"
using System;
using System.Runtime.InteropServices;
public class K { [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h,uint m,IntPtr w,IntPtr l); }
"@
[K]::SendMessage([IntPtr]$args[0],0x0100,[IntPtr]0x09,[IntPtr]::Zero) | Out-Null
