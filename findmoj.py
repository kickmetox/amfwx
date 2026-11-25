from pathlib import Path
for root in ('amfwx','tests','docs','tools','installer'):
    for p in Path(root).rglob('*'):
        if p.suffix.lower() in ('.py','.md','.txt','.yml','.yaml','.toml'):
            try: t=p.read_text(encoding='utf-8')
            except Exception: continue
            if 'Ã' in t or 'â€' in t or 'Â' in t or 'â€“' in t:
                print(p)
