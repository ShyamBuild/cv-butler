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
for k, l in enumerate(L):
    if "ck('S5 board closed row'" in l:
        dd = len(l) - len(l.lstrip())
        L[k+1:k+1] = [dd*' ' + "_src = open(os.path.join(os.path.dirname(os.path.abspath(butler.__file__)), 'butler.py')).read()",
                      dd*' ' + "_h = _src.split('class H(FileSystemEventHandler):')[-1].split('obs = Observer()')[0]",
                      dd*' ' + "ck('S6 watcher handler intact', 'self._add' in _h and 'B._add' not in _h)"]
        done.append('S6-guard'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
q = 'PROTOCOL.md'; P = open(q).read()
if 'blanket self' not in P:
    P = P.rstrip() + "\n9. FORBIDDEN: blanket 'self. -> B.' rewrites by rule. Nested classes (watchdog H inside main) are\n   outside class Butler but NEED self. Fix self/B bugs surgically, one named block at a time.\n"
    open(q, 'w').write(P); done.append('protocol-rule-9')
print('✅', done or 'nothing missing')
