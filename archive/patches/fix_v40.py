import ast, os, subprocess
done = []
p = 'wa.py'; L = open(p).read().split('\n')
if not any(l == 'from playwright.sync_api import sync_playwright' for l in L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def '))
    L[i:i] = ['try:',
              '    from playwright.sync_api import sync_playwright',
              'except Exception:',
              '    sync_playwright = None',
              '']
    done.append('playwright-import-module-level')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
p = 'butler.py'; L = open(p).read().split('\n')
for k, l in enumerate(L):
    if "'S17 playwright import present'" in l:
        d = len(l) - len(l.lstrip())
        L[k] = d*' ' + "ck('S17 playwright import at module scope', any(x == 'from playwright.sync_api import sync_playwright' for x in _wa.split('\\n')))"
        done.append('S17-scope-correct'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
SHIP = open('ship.sh').read()
PRIMARY_COMPANY = 'PRIMARY="/Users/apple/Downloads/Sunsoft Technology"'
if PRIMARY_COMPANY not in SHIP:
    done.append('note: primary set by next promotion')
open('ship.sh.new', 'w').write(SHIP)
r = subprocess.run(['zsh', '-n', 'ship.sh.new'], capture_output=True, text=True)
print('current ship.sh zsh -n:', 'CLEAN' if r.returncode == 0 else 'DIRTY -> will regenerate on promotion step')
print('✅', done or 'nothing missing')
