[Setup]
AppName=AMFWX
AppVersion=1.0.0
DefaultDirName={autopf}\AMFWX
DefaultGroupName=AMFWX
OutputDir=..\dist\installer
OutputBaseFilename=AMFWX-Setup-1.0.0
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\AMFWX.exe

[Files]
Source: "..\dist\AMFWX\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AMFWX"; Filename: "{app}\AMFWX.exe"
Name: "{autodesktop}\AMFWX"; Filename: "{app}\AMFWX.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-VerknÃ¼pfung"

