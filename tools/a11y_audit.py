"""Audit the AMFWX accessibility tree."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from amfwx import (Label, ListBox, RadioButton, SpinBox, Button, CheckBox,
                   LineEdit, Slider, Window)
from amfwx.accessibility import (ROLE_BUTTON, ROLE_CHECKBOX, ROLE_COMBO,
                                 ROLE_EDIT, ROLE_SLIDER, ROLE_UNKNOWN)


INTERACTIVE = {ROLE_BUTTON, ROLE_CHECKBOX, ROLE_EDIT, ROLE_SLIDER, ROLE_COMBO}


def audit(window):
    tree = window.accessibility_tree()
    nodes = list(tree.walk())
    errors = []
    for node in nodes:
        if node.role == ROLE_UNKNOWN:
            errors.append(f"unknown role: {type(node.widget).__name__}")
        if node.role in INTERACTIVE and not node.name:
            errors.append(f"missing name: {type(node.widget).__name__}")
    return {"ok": not errors, "nodes": len(nodes), "errors": errors}


def demo():
    window = Window("A11y Audit", 640, 420)
    window.add(Label("Name"))
    field = LineEdit("")
    field.accessible_name = "Name"
    window.add(field)
    window.add(Button("OK"))
    window.add(CheckBox("Aktiv"))
    window.add(RadioButton("Auswahl"))
    slider = Slider(0, 100, 50)
    slider.accessible_name = "Wert"
    window.add(slider)
    window.add(SpinBox(5))
    window.add(ListBox(["A", "B"]))
    return window


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dist/a11y.json")
    args = parser.parse_args()
    window = demo()
    try:
        result = audit(window)
    finally:
        window.close()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
