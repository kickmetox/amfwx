"""Build a source-portable AMFWX ZIP with install/uninstall scripts."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    import sys
    sys.path.insert(0, str(ROOT))
    import amfwx

    version = amfwx.__version__
    stage = Path(tempfile.mkdtemp(prefix="amfwx-portable-"))
    try:
        shutil.copytree(ROOT / "amfwx", stage / "amfwx",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        if (ROOT / "vendor" / "python32").exists():
            shutil.copytree(ROOT / "vendor" / "python32",
                            stage / "vendor" / "python32",
                            ignore=shutil.ignore_patterns("__pycache__"))
        if (ROOT / "examples").exists():
            shutil.copytree(ROOT / "examples", stage / "examples",
                            ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("README.md", "CHANGELOG.md", "pyproject.toml"):
            source = ROOT / name
            if source.exists():
                shutil.copy2(source, stage / name)
        shutil.copy2(ROOT / "tools" / "install.ps1", stage / "install.ps1")
        shutil.copy2(ROOT / "tools" / "uninstall.ps1", stage / "uninstall.ps1")
        (stage / "AMFWX.cmd").write_text(
            '@echo off\r\ncd /d "%~dp0"\r\npython -m amfwx %*\r\n',
            encoding="utf-8")
        target = ROOT / "dist" / f"AMFWX-Portable-{version}.zip"
        target.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in stage.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(stage))
        print(target)
        return target
    finally:
        shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    main()
