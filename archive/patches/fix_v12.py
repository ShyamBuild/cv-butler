import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []

# 1) rewrite _check_siblings to call _compact_numbers (not just normalize PDFs)
i = next(k for k, l in enumerate(L) if l.strip().startswith('def _check_siblings('))
d = len(L[i]) - len(L[i].lstrip())
j = i + 1
while j < len(L) and not (L[j].strip().startswith('def ') and len(L[j]) - len(L[j].lstrip()) == d):
    j += 1
L[i:j] = [d*' ' + 'def _check_siblings(self, folder):',
          d*' ' + '    if not os.path.isdir(folder): return',
          d*' ' + '    try:',
          d*' ' + '        self._compact_numbers(folder, print)',
          d*' ' + '    except Exception as e:',
          d*' ' + '        print(f"⚠️ compact error in {folder}: {e}")',
          '']
done.append('check-siblings-calls-compact')

# 2) add _compact_numbers to the heartbeat sweep (every 2 min, every folder)
for k, l in enumerate(L):
    if 'sweep #' in l and 'print' in l:
        dd = len(l) - len(l.lstrip())
        # insert after the sweep print
        L.insert(k+1, dd*' ' + 'try:')
        L.insert(k+2, dd*' ' + '    for dp, dn, fn in os.walk(self.root):')
        L.insert(k+3, dd*' ' + '        dn[:] = [x for x in dn if not x.startswith(".")]'  )
        L.insert(k+4, dd*' ' + '        self._compact_numbers(dp, print)')
        L.insert(k+5, dd*' ' + 'except Exception as _ce:')
        L.insert(k+6, dd*' ' + '    print(f"compact sweep error: {_ce}")')
        done.append('heartbeat-compacts-all')
        break

new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done)
