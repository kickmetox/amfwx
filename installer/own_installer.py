"""AMFWX own installer (no Inno Setup)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

APP_NAME = "AMFWX"
APP_VERSION = "5.10.0"


def payload_path():
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return Path(base) / "payload.zip"


def default_target():
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / "Programs" / APP_NAME


def _shortcut(target, name):
    desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
    start = (Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" /
             "Start Menu" / "Programs")
    script = f'''
$ws = New-Object -ComObject WScript.Shell
foreach ($dir in @("{desktop}", "{start}")) {{
  $path = Join-Path $dir "{name}.lnk"
  $shortcut = $ws.CreateShortcut($path)
  $shortcut.TargetPath = "{target}"
  $shortcut.WorkingDirectory = "{Path(target).parent}"
  $shortcut.Save()
}}
'''
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-Command", script], capture_output=True)


def install(target=None):
    target = Path(target) if target else default_target()
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(payload_path()) as archive:
        archive.extractall(target)
    exe = target / "AMFWX.exe"
    if not exe.exists():
        raise RuntimeError("Payload enthält AMFWX.exe nicht")
    _shortcut(exe, APP_NAME)
    uninstall = target / "uninstall.cmd"
    uninstall.write_text(
        "@echo off\r\n"
        "reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\"
        "Uninstall\\AMFWX\" /f >nul 2>&1\r\n"
        "del \"%USERPROFILE%\\Desktop\\AMFWX.lnk\" >nul 2>&1\r\n"
        "del \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\"
        "AMFWX.lnk\" >nul 2>&1\r\n"
        f'rmdir /s /q "{target}"\r\n' ,
        encoding="utf-8")
    import winreg
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion"
                           r"\Uninstall\AMFWX")
    with key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ,
                          APP_VERSION)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ,
                          str(target))
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "AMFWX")
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ,
                          f'cmd /c "{uninstall}"')
    return target


def uninstall(target=None):
    target = Path(target) if target else default_target()
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    import winreg
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion"
                         r"\Uninstall\AMFWX")
    except FileNotFoundError:
        pass
    for path in (
        Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "AMFWX.lnk",
        Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" /
        "Start Menu" / "Programs" / "AMFWX.lnk",
    ):
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def gui():
    from amfwx import Button, Label, LineEdit, Window, BoxLayout
    window = Window("AMFWX installieren", 560, 260)
    window.layout = BoxLayout(spacing=10, padding=18)
    window.root.children.clear()
    window.root.add(Label("Zielordner", scale=2))
    path = LineEdit(str(default_target()))
    window.root.add(path)
    status = Label("Bereit", scale=1)
    window.root.add(status)

    def do_install():
        try:
            target = install(path.text())
            status.text = f"Installiert: {target}"
        except Exception as error:
            status.text = f"Fehler: {error}"

    window.root.add(Button("Installieren", on_click=do_install,
                           variant="primary"))
    window.root.add(Button("Beenden", on_click=window.close))
    window._layout_root()
    return window.run()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    silent = "/S" in argv or "--silent" in argv
    target = None
    for argument in argv:
        if argument.startswith("/D="):
            target = argument[3:].strip('"')
        elif argument.startswith("--target="):
            target = argument.split("=", 1)[1].strip('"')
    if silent:
        try:
            install(target)
            return 0
        except Exception as error:
            print(error, file=sys.stderr)
            return 1
    return gui()


if __name__ == "__main__":
    raise SystemExit(main())
