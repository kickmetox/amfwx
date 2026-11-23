"""MTP/PTP camera inventory and image download via Windows Shell."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class MtpError(RuntimeError):
    pass


def _powershell(script, timeout=120):
    process = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-Command", script],
        capture_output=True, text=True, timeout=timeout)
    if process.returncode != 0:
        raise MtpError(process.stderr.strip() or "PowerShell-Fehler")
    return process.stdout


def list_mtp_devices():
    script = r'''
$shell = New-Object -ComObject Shell.Application
$items = $shell.Namespace(17).Items()
$list = @()
foreach ($item in $items) {
  if ($item.IsFolder -and $item.Path -notmatch '^[A-Za-z]:\\') {
    $list += [pscustomobject]@{ name = $item.Name; path = $item.Path }
  }
}
$list | ConvertTo-Json -Compress
'''
    output = _powershell(script, timeout=30).strip()
    if not output:
        return []
    data = json.loads(output)
    if isinstance(data, dict):
        data = [data]
    from .camera import list_pnp_cameras
    names = [camera.name.lower() for camera in list_pnp_cameras()]
    result = []
    for item in data:
        name = str(item.get("name", ""))
        lower = name.lower()
        if any(lower == known or lower in known or known in lower
               for known in names):
            result.append({"name": name,
                           "path": str(item.get("path", ""))})
    return result


def _quote(value):
    return str(value).replace("'", "''")


def download_images(device_name, destination, timeout=300):
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=True)
    script = f'''
$shell = New-Object -ComObject Shell.Application
$name = '{_quote(device_name)}'
$destPath = '{_quote(target)}'
$device = $shell.Namespace(17).Items() | Where-Object {{ $_.Name -eq $name }} | Select-Object -First 1
if (-not $device) {{ Write-Error "device not found"; exit 2 }}
$dest = $shell.Namespace($destPath)
$count = 0
function Copy-Images($folder) {{
  foreach ($item in $folder.Items()) {{
    if ($item.IsFolder) {{
      Copy-Images $item.GetFolder
    }} elseif ($item.Name -match '\\.(jpg|jpeg|png|tif|tiff|heic|dng|cr2|nef|arw|raf|orf)$') {{
      $dest.CopyHere($item, 0x10)
      $script:count++
    }}
  }}
}}
Copy-Images $device.GetFolder
$count
'''
    output = _powershell(script, timeout=timeout).strip().splitlines()
    try:
        count = int(output[-1]) if output else 0
    except ValueError:
        count = 0
    return count
