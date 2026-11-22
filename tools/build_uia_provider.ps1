$path = "D:\PRG\mingw64\bin\g++.exe"
if (-not (Test-Path $path)) { throw "MinGW g++ nicht gefunden: $path" }
& $path -std=c++17 -O2 -shared -static -static-libgcc -static-libstdc++ `
  -o native\uia_provider.dll native\uia_provider.cpp `
  -luiautomationcore -lole32 -loleaut32 -luuid -luser32
if ($LASTEXITCODE -ne 0) { throw "UIA-Provider-Build fehlgeschlagen" }
Copy-Item native\uia_provider.dll amfwx\bin\uia_provider.dll -Force
Write-Host "uia_provider.dll gebaut"
