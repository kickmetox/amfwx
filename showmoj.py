from pathlib import Path
for p in [Path('amfwx/editor.py'),Path('tests/test_advanced_widgets.py'),Path('docs/own_installer.md'),Path('docs/release_2.5.2.md')]:
    print('---',p)
    for i,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if 'Ã' in line or 'â€' in line or 'Â' in line:
            print(i,line[:200])
