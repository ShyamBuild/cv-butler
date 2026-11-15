import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip() == 'self._rename_clean()' and ind(l) == 4:  # main-body only; the tick's method-scope call at 1410 is legitimate
        d = ind(l)
        B[k:k+1] = [d*' ' + "_rc = getattr(B, '_rename_clean', None)  # RENAME-CLEAN-CALL v81.45: main has no self; a wounded pass may never kill the watcher",
                    d*' ' + "if _rc:",
                    (d+4)*' ' + "try: _rc()",
                    (d+4)*' ' + "except Exception as _rce: print(f'⚠️ rename-clean skipped this pass: {_rce}', flush=True)"]
        done.append('rename-clean-call-fixed'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S165 main never speaks self" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S164 the heal runs in every mode" in l]
    if not anch: anch = [k for k, l in enumerate(B) if "'S163 a failed rename speaks its reason" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S165 main never speaks self', not any(x.startswith('    self.') and not x.startswith('     ') for x in _src.split(chr(10))))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S165-guard')
print('✅', done)
