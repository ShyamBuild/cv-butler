import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# SKIP-FIX v74' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'def _route(self, p, say):')
    B[i] = ind(B[i])*' ' + 'def _route(self, p, say, skip_tags=None):'
    B.insert(i+1, ind(B[i])*' ' + "sk = skip_tags if skip_tags is not None else getattr(self, '_skip_tags', False)  # SKIP-FIX v74")
    done.append('route-skip-param')
src = '\n'.join(B)
old = "if not getattr(self, '_skip_tags', False): self.handle_tags(p, say)"
if old in src:
    i = next(k for k, l in enumerate(B) if l.strip() == old)
    B[i] = ind(B[i])*' ' + 'if not sk: self.handle_tags(p, say)'
    done.append('route-skip-local')
src = '\n'.join(B)
n = 0
for k, l in enumerate(B):
    if l.strip() in ('self._route(fp, say)', 'self._route(p, say)') and 'skip_tags' not in l:
        B[k] = ind(l)*' ' + l.strip().replace(')', ', skip_tags=False)'); n += 1
if n: done.append(f'callers-explicit-x{n}')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S95 tag-skip is per-call not per-instance" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S94 client-root block on live path" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S95 tag-skip is per-call not per-instance', 'skip_tags=None' in _src and _src.count('skip_tags=False') >= 2 and (chr(35)+' SKIP-FIX') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S95-guard')
print('✅', done)
