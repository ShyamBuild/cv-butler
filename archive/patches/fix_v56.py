import ast, re
p = 'butler.py'; L = open(p).read().split('\n')
done, skipped = [], []
def P(L):
    try: ast.parse('\n'.join(L)); return True
    except Exception: return False
def ind(l): return len(l) - len(l.lstrip())
def edit(name, func):
    global L
    try: L2 = func(list(L))
    except Exception: skipped.append(name + ':anchor'); return
    if not L2 or L2 == L: skipped.append(name + ':nochange'); return
    if not P(L2): skipped.append(name + ':syntax'); return
    L = L2; done.append(name)
def e1(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def route(self'))
    if 'self.heat' in '\n'.join(L[i:i+4]): return L
    pname = L[i].strip().split('(')[1].split(')')[0].split(',')[1].strip().split('=')[0]
    d = ind(L[i])
    L.insert(i+1, d*' ' + "    try: self.heat = getattr(self, 'heat', {}); self.heat[self.position_folder_for(" + pname + ")] = time.time()")
    L.insert(i+2, d*' ' + '    except Exception: pass')
    return L
def e2(L):
    for k, l in enumerate(L):
        if l.strip().startswith('def _reconcile_tags(self'):
            if 'dirs' in l: return L
            if l.rstrip().endswith('):'):
                L[k] = l.rstrip()[:-2] + ', dirs=None):'
            return L
    return L
def e3(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _reconcile_tags(self'))
    w = next(k for k in range(i+1, min(i+40, len(L))) if 'os.walk(self.root)' in L[k])
    if 'os.walk(_d0)' in '\n'.join(L[w:w+3]): return L
    wi = ind(L[w]); j = w + 1
    while j < len(L) and (not L[j].strip() or ind(L[j]) > wi): j += 1
    L[w:j] = [wi*' ' + 'for _d0 in (dirs or [self.root]):'] + [((ind(x)+2) if x.strip() else 0)*' ' + x.strip() for x in L[w+1:j]]
    return L
def e4(L):
    if 'def sweep_dirs(self' in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _reconcile_tags(self'))
    d = ind(L[i])
    L[i:i] = [d*' ' + 'def sweep_dirs(self, n):',
              d*' ' + '    now = time.time()',
              d*' ' + '    dirs = []',
              d*' ' + '    f = None',
              d*' ' + '    try:',
              d*' ' + '        import briefing as _b',
              d*' ' + '        fz = _b._read_focus()',
              d*' ' + "        f = fz['path'] if fz else None",
              d*' ' + '    except Exception:',
              d*' ' + '        f = None',
              d*' ' + '    if f and f.startswith(self.root): dirs.append(f)',
              d*' ' + "    for pp, tt in list(getattr(self, 'heat', {}).items()):",
              d*' ' + '        if now - tt < 1800 and pp not in dirs and pp.startswith(self.root): dirs.append(pp)',
              d*' ' + '    if n % 3 == 0:',
              d*' ' + '        for pp in list(dirs):',
              d*' ' + '            cc = os.path.dirname(pp)',
              d*' ' + '            if cc not in dirs and cc.startswith(self.root): dirs.append(cc)',
              d*' ' + '    if n % 9 == 0 or not dirs: dirs = [self.root]',
              d*' ' + '    return dirs',
              '']
    return L
def e5(L):
    for k, l in enumerate(L):
        if l.strip().startswith('B._reconcile_tags(') and 'sweep_dirs' not in l:
            L[k] = re.sub(r'B\._reconcile_tags\((hsay|print)\)', 'B._reconcile_tags(hsay, B.sweep_dirs(n))', l)
            return L
    return L
def e6(L):
    if "'S20 sweep scoping" in '\n'.join(L): return L
    i = next(k for k, l in enumerate(L) if "'S19 reconcile adds no company-root tag folders'" in l)
    d = ind(L[i])
    L.insert(i+1, d*' ' + "ck('S20 sweep scoping + heat net intact', 'def sweep_dirs(self' in _src and 'n % 9 == 0 or not dirs' in _src)")
    return L
edit('route-heat', e1)
edit('reconcile-signature', e2)
edit('reconcile-walk-scoped', e3)
edit('sweep-dirs-method', e4)
edit('sweep-call-site', e5)
edit('S20-guard', e6)
open(p, 'w').write('\n'.join(L))
print('✅ applied:', done)
print('⏭ skipped:', skipped or 'none')
