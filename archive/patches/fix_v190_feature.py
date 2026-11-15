import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# RENAME-IN-TICK v81.52' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _autodraft_tick(self, say=print):'))
    d = ind(B[i]) + 4
    B[i+1:i+1] = [d*' ' + "if not getattr(self, '_rc_boot', False):  # RENAME-IN-TICK v81.52: the heal runs where every mode actually executes",
                  d*' ' + "    self._rc_boot = True",
                  d*' ' + "    try:",
                  d*' ' + "        _rn = self._rename_clean()",
                  d*' ' + "        if _rn: print(f'✏️[rename-clean] boot pass renamed {_rn} file(s)', flush=True)",
                  d*' ' + "    except Exception as _rce3:",
                  d*' ' + "        print(f'⚠️[rename-clean] boot pass skipped: {_rce3}', flush=True)"]
    done.append('rename-in-tick')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S164 the heal runs in every mode" not in '\n'.join(B):
    anch = [k for k, l in enumerate(B) if "'S163 a failed rename speaks its reason" in l]
    i = anch[-1]; d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S164 the heal runs in every mode', (chr(35)+' RENAME-IN-TICK v81.52') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S164-guard')
print('✅', done)
