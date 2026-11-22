"""Deterministic UI snapshot tool."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from amfwx import Button, Label, TableView, TextEdit, Window  # noqa: E402


def snapshot(path, theme="dark"):
    window = Window("Snapshot", 640, 400, theme=theme)
    window.root.children.clear()
    window.root.add(Label("AMFWX Snapshot"))
    window.root.add(Button("Aktion"))
    window.root.add(TextEdit("Text"))
    window.root.add(TableView(["A", "B"], [["1", "2"], ["3", "4"]]))
    window._layout_root()
    window.render_to_png(path)
    window.close()
    window.process_events(40)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv):
    baseline_path = ROOT / "tests" / "baselines" / "snapshot.json"
    update = "--update" in argv
    output_dir = ROOT / "tests" / "baselines"
    output_dir.mkdir(parents=True, exist_ok=True)
    themes = ("dark", "light", "high_contrast")
    current = {}
    for theme in themes:
        output = output_dir / f"snapshot_{theme}.png"
        snapshot(output, theme)
        current[theme] = digest(output)
        print(f"{theme}: {current[theme]}")
    if update or not baseline_path.exists():
        baseline_path.write_text(json.dumps(current, indent=2),
                                 encoding="utf-8")
        return 0
    expected = json.loads(baseline_path.read_text(encoding="utf-8"))
    return 0 if expected == current else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
