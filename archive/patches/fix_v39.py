import ast
done = []
p = 'wa.py'; L = open(p).read().split('\n')
if 'from playwright.sync_api import sync_playwright' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def '))
    L[i:i] = ['try:',
              '    from playwright.sync_api import sync_playwright',
              'except Exception:',
              '    sync_playwright = None',
              '']
    done.append('playwright-import')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
p = 'butler.py'; L = open(p).read().split('\n')
if "'S17 playwright import present'" not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if "'S16 verified auto-fill'" in l)
    d = len(L[i]) - len(L[i].lstrip())
    L.insert(i+1, d*' ' + "ck('S17 playwright import present', 'from playwright.sync_api import sync_playwright' in _wa)")
    done.append('S17-guard')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
s = open('ship.sh').read().split('\n')
for k, l in enumerate(s):
    if l.startswith('PRIMARY='):
        s[k] = 'PRIMARY="/Users/apple/Downloads/Sunsoft Technology"'
        done.append('ship-primary-company'); break
old = '  if [ ${#LIVE_ROOTS[@]} -eq 0 ]; then LIVE_ROOTS=("$ROOT"); fi'
newblk = ['  keep=()',
          '  for rt in "${LIVE_ROOTS[@]}"; do',
          '    case "$rt" in "$ROOT"/*|"$ROOT") ;; *) keep+=("$rt") ;; esac',
          '  done',
          '  LIVE_ROOTS=("$ROOT" "${keep[@]}")']
for k, l in enumerate(s):
    if l.strip() == old.strip():
        s[k:k+1] = newblk
        done.append('resume-collapses-into-company'); break
open('ship.sh', 'w').write('\n'.join(s))
P = open('PROTOCOL.md').read()
if 'company-wide watcher' not in P:
    P = P.rstrip() + '\n12. ONE company-wide watcher (~/Downloads/Sunsoft Technology, recursive) does all silent work; focus narrows briefs/commands to one position. Never launch per-position butlers while it runs (locks refuse). Other Sunsoft trees elsewhere are out of scope.\n'
    open('PROTOCOL.md', 'w').write(P); done.append('protocol-rule-12')
print('✅', done or 'nothing missing')
