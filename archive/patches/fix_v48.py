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
def p1(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def position_folder_for('))
    d = ind(L[i]); j = i + 1
    while j < len(L) and (not L[j].strip() or ind(L[j]) > d): j += 1
    L[i:j] = [d*' ' + 'def position_folder_for(self, p):',
              d*' ' + '    dd = os.path.dirname(os.path.abspath(p))',
              d*' ' + '    rel = os.path.relpath(dd, self.root)',
              d*' ' + "    parts = [] if rel == '.' else rel.split(os.sep)",
              d*' ' + '    if len(parts) >= 2:',
              d*' ' + '        return os.path.join(self.root, parts[0], parts[1])',
              d*' ' + '    return dd', '']
    return L
def s0(L):
    if '_ROOTTAGS0' in '\n'.join(L): return L
    k = next(x for x, l in enumerate(L) if l.strip().startswith('def _selftest('))
    d = ind(L[k])
    L[k+1:k+1] = [d*' ' + "    _tg0 = {t.lower().replace('\\u2013','-').replace(' ','_') for t in ['Awaiting CV Update','Awaiting JD Confirmation','Call Scheduled','Feedback Pending','Interview Scheduled','Closed – Not Proceeding','Ready for Manager Review','Rejected by Client']}",
                  d*' ' + "    _ROOTTAGS0 = {c for c in os.listdir(root) if os.path.isdir(os.path.join(root, c)) and c.lower().replace('\\u2013','-').replace(' ','_') in _tg0}"]
    return L
def s1(L):
    if "ck('S1 " in '\n'.join(L): return L
    i0 = next(k for k, l in enumerate(L) if l.strip().startswith('def _selftest('))
    i1 = i0 + 1
    while i1 < len(L) and not (L[i1].strip().startswith('def ') and not ind(L[i1])): i1 += 1
    seg = L[i0:i1]
    a = next(k for k, l in enumerate(seg) if '= Butler(' in l)
    d = ind(seg[a])
    seg[a+1:a+1] = [d*' ' + "ck('S1 bindings', all(callable(getattr(B, m, None)) for m in ('route','handle_tags','_reconcile_tags','_compact_numbers','position_folder_for','tags_of')))"]
    L[i0:i1] = seg
    return L
def s5(L):
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
        l = l.replace('os.path.join(root, tag', 'os.path.join(POS, tag)')
        l = l.replace('collect(root)', 'collect(POS)')
        l = l.replace('print_briefing(root)', 'print_briefing(POS)')
        out.append(l)
    L[i0:i1] = out
    return L
def s17(L):
    for k, l in enumerate(L):
        if "'S17 playwright import" in l:
            L[k] = ind(l)*' ' + "ck('S17 playwright import at module scope', 'try:\\n    from playwright.sync_api import sync_playwright' in _wa)"
            return L
    return L
def s18(L):
    if "'S18 position never falls back" in '\n'.join(L): return L
    k = next(x for x, l in enumerate(L) if "'S17 playwright import" in l)
    d = ind(L[k])
    L[k+1:k+1] = [d*' ' + "ck('S18 position never falls back to company root', 'return os.path.join(self.root, parts[0], parts[1])' in _src and 'return self.root' not in _src.split('def position_folder_for')[1].split('def ')[0])",
                  d*' ' + "ck('S19 reconcile adds no company-root tag folders', not [c for c in os.listdir(root) if os.path.isdir(os.path.join(root, c)) and c.lower().replace('\\u2013','-').replace(' ','_') in _tg0 and c not in _ROOTTAGS0])"]
    return L
def s12(L):
    src = '\n'.join(L)
    if "ck('S12 send phase" in src: return L
    for k, l in enumerate(L):
        if "ck('S16 send phase launches+fills'" in l:
            L[k] = l.replace("ck('S16 send phase launches+fills'", "ck('S12 send phase launches+fills'")
            return L
    return L
edit('wa.py', 'playwright-import-module-level', w1)
edit('butler.py', 'position-folder-depth2', p1)
edit('butler.py', 'selftest-root-tag-snapshot', s0)
edit('butler.py', 'S1-bindings-restored', s1)
edit('butler.py', 'selftest-root-agnostic', s5)
edit('butler.py', 'S17-pair-check', s17)
edit('butler.py', 'S18-S19-guards', s18)
edit('butler.py', 'S12-label-restored', s12)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
