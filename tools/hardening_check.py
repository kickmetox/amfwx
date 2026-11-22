"""Release hardening checks for AMFWX.

Run:
    python tools/hardening_check.py
    python tools/hardening_check.py --no-tests
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REQUIRED_BINARIES = [
    "amfwx/bin/mfdecode.dll",
    "amfwx/bin/uia_provider.dll",
    "amfwx/bin/SDL3.dll",
    "amfwx/bin/libwebp.dll",
    "amfwx/bin/libsharpyuv.dll",
    "amfwx/bin/checksums.json",
]

REQUIRED_FILES = [
    "amfwx/__init__.py",
    "amfwx/accessibility.py",
    "amfwx/uia_native.py",
    "amfwx/mediaplayer.py",
    "amfwx/advanced.py",
    "amfwx/models.py",
    "amfwx/quick.py",
    "amfwx/animation.py",
    "amfwx/midi.py",
    "amfwx/resources.py",
    "amfwx/crash.py",
    "amfwx/security.py",
    "amfwx/ai.py",
    "amfwx/llm_tools.py",
    "amfwx/agent.py",
    "amfwx/sdk.py",
    "amfwx/dsp.py",
    "amfwx/mixer.py",
    "native/uia_provider.cpp",
    "native/mfdecode.cpp",
]


def check_binaries():
    errors = []
    for relative in REQUIRED_BINARIES:
        path = ROOT / relative
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"fehlt: {relative}")
    return errors


def check_files():
    errors = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            errors.append(f"fehlt: {relative}")
    return errors


def check_compile():
    result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "amfwx"],
        cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return [result.stdout + result.stderr]
    return []


def check_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT, capture_output=True, text=True)
    tail = "\n".join((result.stdout + result.stderr).splitlines()[-6:])
    if result.returncode != 0:
        return [tail]
    return []


def scan_patterns():
    warnings = []
    patterns = {
        "eval(": "eval",
        "exec(": "exec",
        "os.system(": "os.system",
        "shell=True": "shell=True",
        "except:": "bare except",
    }
    for path in (ROOT / "amfwx").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle, label in patterns.items():
            for number, line in enumerate(text.splitlines(), 1):
                if needle in line and not line.lstrip().startswith("#"):
                    warnings.append(
                        f"{path.relative_to(ROOT)}:{number}: {label}")
    return warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tests", action="store_true")
    args = parser.parse_args()

    failures = []
    failures.extend(check_files())
    failures.extend(check_binaries())
    failures.extend(check_compile())
    if not args.no_tests:
        failures.extend(check_tests())
    warnings = scan_patterns()

    import amfwx
    print(f"AMFWX {amfwx.__version__}")
    print(f"Tests: {'übersprungen' if args.no_tests else 'ausgeführt'}")
    print(f"Warnungen: {len(warnings)}")
    for warning in warnings:
        print(f"  WARN {warning}")
    if failures:
        print("FEHLER:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("Härtungscheck: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
