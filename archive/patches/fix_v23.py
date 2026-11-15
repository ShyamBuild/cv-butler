import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
i = next(k for k, l in enumerate(L) if 'class H(FileSystemEventHandler):' in l)
d = len(L[i]) - len(L[i].lstrip())
j = i + 1
while j < len(L) and (not L[j].strip() or (len(L[j]) - len(L[j].lstrip())) > d):
    j += 1
n = 0
for k in range(i, j):
    if 'B._add(' in L[k]:
        L[k] = L[k].replace('B._add(', 'self._add('); n += 1
if n: done.append(f'watcher-self-restored x{n}')
if not any('S6 watcher handler intact' in l for l in L):
    for k, l in enumerate(L):
        if "ck('S5 board closed row'" in l:
            dd = len(l) - len(l.lstrip())
            L[k+1:k+1] = [dd*' ' + "import ast as _ast",
                          dd*' ' + "_ln = open(__file__).read().split('\\n')",
                          dd*' ' + "_hcls = [x for x in _ast.walk(_ast.parse('\\n'.join(_ln))) if isinstance(x, _ast.ClassDef) and x.name == 'H']",
                          dd*' ' + "_seg = '\\n'.join(_ln[_hcls[0].lineno-1:_hcls[0].end_lineno]) if _hcls else ''",
                          dd*' ' + "ck('S6 watcher handler intact', bool(_seg) and 'self._add' in _seg and 'B._add' not in _seg, f'seglen={len(_seg)}')"]
            done.append('S6-ast-based'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
