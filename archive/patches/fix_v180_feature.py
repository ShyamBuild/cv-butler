import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip() == 'self._rename_clean()':
        d = ind(l)
        B[k:k+1] = [d*' ' + "_rc = getattr(B, '_rename_clean', None)  # RENAME-CLEAN-CALL v81.45: main has no self; call the instance, guarded",
                    d*' ' + "if _rc:",
                    (d+4)*' ' + "try: _rc()",
                    (d+4)*' ' + "except Exception as _rce: print(f'⚠️ rename-clean: {_rce}', flush=True)"]
        done.append('rename-clean-call-fixed'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S148 main never speaks self" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S147 the same draft never enters the same chat twice" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S148 main never speaks self', not any(x.startswith('    self.') and not x.startswith('     ') for x in _src.split(chr(10))))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S148-guard')
print('✅', done)
