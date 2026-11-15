import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
mi = next(k for k, l in enumerate(L) if l.startswith('def main('))
for i in range(mi, len(L)):
    if 'self._compact_numbers' in L[i]:
        L[i] = L[i].replace('self._compact_numbers', 'B._compact_numbers')
        done.append('sweep-compact-uses-B')
    if 'self._reconcile_tags' in L[i]:
        L[i] = L[i].replace('self._reconcile_tags', 'B._reconcile_tags')
        done.append('sweep-reconcile-uses-B')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
