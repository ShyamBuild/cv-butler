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
            L[k+1:k+1] = [dd*' ' + "_src = open(__file__).read()",
                          dd*' ' + "_h = _src.split('class H(FileSystemEventHandler):')[-1].split('obs = Observer()')[0]",
                          dd*' ' + "ck('S6 watcher handler intact', 'self._add' in _h and 'B._add' not in _h)"]
            done.append('S6-guard-self-contained'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
