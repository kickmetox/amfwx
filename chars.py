from pathlib import Path
p=Path('amfwx/editor.py'); t=p.read_text(encoding='utf-8')
for ch in sorted(set(t)):
    if ord(ch)>127: print(repr(ch), hex(ord(ch)))
