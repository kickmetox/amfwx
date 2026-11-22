# AMFWX 3.23.0

AMFWX 3.23 fixes a real layout/accessibility bug.

## Fix

`window.layout.add(...)` now synchronizes the root widget tree. Before this,
widgets added through the layout were arranged but not painted or exposed
in the accessibility tree.

## New

- root synchronization in `Window._layout_root`
- no duplicate children
- tests for layout/root/accessibility consistency
- 216 tests

## Assets

- `amfwx-3.23.0-py3-none-any.whl`
- `AMFWX-Portable-3.23.0.zip`
- `AMFWX-Own-Setup-3.23.0.exe` (unsigned)
- `SHA256SUMS.txt`
