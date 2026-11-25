from pathlib import Path
for p in [Path('amfwx/editor.py'),Path('tests/test_advanced_widgets.py'),Path('docs/own_installer.md'),Path('docs/release_2.5.2.md')]:
    print('---',p)
    for i,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if any(c in line for c in ('Ã','â','Â')):
            print(i,repr(line))
