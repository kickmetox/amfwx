# Native UIA provider build

The native UIA provider is `native/uia_provider.cpp`. It is built with the
WinLibs MinGW toolchain at `D:\PRG\mingw64`.

## Script

```powershell
powershell -ExecutionPolicy Bypass -File tools\build_uia_provider.ps1
```

The script writes:

- `native/uia_provider.dll`
- `amfwx/bin/uia_provider.dll`

## Manual build

```powershell
& "D:\PRG\mingw64\bin\g++.exe" `
  -std=c++17 -O2 -shared -static `
  -static-libgcc -static-libstdc++ `
  -o native\uia_provider.dll native\uia_provider.cpp `
  -luiautomationcore -lole32 -loleaut32 -luuid -luser32
```

## Static runtime

`-static` avoids dependencies on:

- `libstdc++-6.dll`
- `libgcc_s_seh-1.dll`

The DLL can therefore ship in the wheel and portable ZIP without extra
runtime files.

## Interfaces

- `IRawElementProviderSimple`
- `IRawElementProviderFragment`
- `IInvokeProvider`
- `IValueProvider`
- `IToggleProvider`

## Routing

```text
MSAA: -1, -4, 0      → native MSAA provider
UIA:  all other ids  → UiaReturnRawElementProvider
```

## Exports

- `amfwx_uia_attach`
- `amfwx_uia_set_name`
- `amfwx_uia_set_bounds`
- `amfwx_uia_notify_focus`
- `amfwx_uia_notify_structure`
- `amfwx_uia_notify_name`
- `amfwx_uia_detach`
