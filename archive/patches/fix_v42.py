import ast
rep = {f: open(f).read().split('\n') for f in ('wa.py', 'butler.py')}
done, skipped = [], []
def P(L):
    try: ast.parse('\n'.join(L)); return True
    except Exception: return False
def ind(l): return len(l) - len(l.lstrip())
def edit(fn_, name, func):
    L = rep[fn_]
    try: L2 = func(list(L))
    except Exception: skipped.append(name + ':anchor'); return
    if not L2 or L2 == L: skipped.append(name + ':nochange'); return
    if not P(L2): skipped.append(name + ':syntax'); return
    rep[fn_] = L2; done.append(name)
def w1(L):
    if 'try:\n    from playwright.sync_api import sync_playwright' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def ') and not ind(l))
    L[i:i] = ['try:', '    from playwright.sync_api import sync_playwright', 'except Exception:', '    sync_playwright = None', '']
    return L
edit('wa.py', 'playwright-import-module-level', w1)
def b1(L):
    for k, l in enumerate(L):
        if "'S17 playwright import" in l:
            L[k] = ind(l)*' ' + "ck('S17 playwright import at module scope', 'try:\\n    from playwright.sync_api import sync_playwright' in _wa)"
            return L
    return L
edit('butler.py', 'S17-pair-check', b1)
def b2(L):
    i0 = next(k for k, l in enumerate(L) if l.strip().startswith('def _selftest('))
    i1 = i0 + 1
    while i1 < len(L) and not (L[i1].strip().startswith('def ') and not ind(L[i1])): i1 += 1
    seg = L[i0:i1]
    if 'POS = os.path.dirname(os.path.dirname(' in '\n'.join(seg): return L
    a = next(k for k, l in enumerate(seg) if "'Pradip Amte.pdf'" in l)
    d = ind(seg[a])
    seg[a+1:a+1] = [d*' ' + "_prw = [os.path.join(dp, f) for dp, dn, fn in os.walk(root) for f in fn if f == 'Pradip Amte.pdf']",
                    d*' ' + 'POS = os.path.dirname(os.path.dirname(_prw[0])) if _prw else root']
    out = []
    for l in seg:
        l = l.replace('os.path.join(root, tag', 'os.path.join(POS, tag')
        l = l.replace('collect(root)', 'collect(POS)')
        l = l.replace('print_briefing(root)', 'print_briefing(POS)')
        out.append(l)
    L[i0:i1] = out
    return L
edit('butler.py', 'selftest-root-agnostic', b2)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
