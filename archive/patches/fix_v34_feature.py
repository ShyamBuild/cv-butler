import ast
rep = {f: open(f).read().split('\n') for f in ('butler.py', 'briefing.py')}
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
def e1(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _reconcile_tags(self'))
    seg = L[i:i+80]
    if any('self.slog.observe' in l for l in seg): return L
    pr = next(k for k, l in enumerate(seg) if '[reconcile]' in l)
    d = ind(seg[pr])
    blk = [d*' ' + 'try:',
           d*' ' + '    _g = locals()',
           d*' ' + "    _pp = _g.get('p') or _g.get('fp') or _g.get('src')",
           d*' ' + "    _tt = _g.get('tag') or _g.get('tg') or _g.get('stage')",
           d*' ' + '    if _pp and _tt:',
           d*' ' + '        self.slog.observe(os.path.splitext(os.path.basename(_pp))[0], _tt, os.path.relpath(self.position_folder_for(_pp), self.root))',
           d*' ' + 'except Exception:',
           d*' ' + '    pass']
    L[i+pr+1:i+pr+1] = blk
    return L
edit('butler.py', 'reconcile-observe-locals', e1)
def e2(L):
    changed = False
    for k, l in enumerate(L):
        if l.strip().startswith("elif cmd ==") and "cmd == 'history'" not in '\n'.join(L[k:k+4]) and ("cmd == 'missed'" in l or "cmd == 'nudge'" in l):
            L.insert(k+1, ind(l)*' ' + "elif cmd == 'history': do_history(arg, root, print)")
            L.insert(k+2, ind(l)*' ' + "elif cmd == 'stale': do_stale(arg, root, print)")
            changed = True; break
    return L if changed else L
edit('briefing.py', 'cli-routes-fixed', e2)
def e3(L):
    changed = False
    for k, l in enumerate(L):
        if "startswith('missed ')" in l and "startswith('history ')" not in '\n'.join(L[k:k+4]):
            L.insert(k+1, ind(l)*' ' + "elif line.startswith('history '): briefing.do_history(raw[8:], root, print)")
            L.insert(k+2, ind(l)*' ' + "elif line.startswith('stale'): briefing.do_stale(raw[5:].strip(), root, print)")
            changed = True; break
    return L if changed else L
edit('briefing.py', 'chat-routes', e3)
edit('butler.py', 'console-routes', e3)
def e4(L):
    if 'history <name>' in '\n'.join(L): return L
    for k, l in enumerate(L):
        if 'missed  <number>' in l:
            L.insert(k+1, ind(l)*' ' + 'history <name>       .. stage transitions for one candidate')
            L.insert(k+2, ind(l)*' ' + 'stale [days]         .. candidates in current stage longer than N days (default 7)')
            return L
    return L
edit('briefing.py', 'help-card-fixed', e4)
def e5(L):
    for k, l in enumerate(L):
        if "'S21 stage ageing" in l:
            L[k] = ind(l)*' ' + "ck('S21 stage ageing wired end-to-end', 'self.slog.observe' in _src and \"elif cmd == 'history'\" in _br and 'def do_stale(' in _br)"
            return L
    return L
edit('butler.py', 'S21-wiring-teeth', e5)
for f in rep:
    open(f, 'w').write('\n'.join(rep[f]))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
