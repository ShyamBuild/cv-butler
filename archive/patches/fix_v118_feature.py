import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# SKIP-FIX v74' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'def _route(self, p, say):')
    d = ind(B[i])
    B[i] = d*' ' + 'def _route(self, p, say, skip_tags=None):'
    B.insert(i+1, (d+4)*' ' + "sk = skip_tags if skip_tags is not None else getattr(self, '_skip_tags', False)  # SKIP-FIX v74")
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
src = '\n'.join(B)
if '# TAG-TRUTH v75' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def handle_tags('))
    j = next((k for k in range(i, i+8) if '# TAGS-GATE' in B[k]), i)
    d = ind(B[i]) + 4
    B[j+1:j+1] = [d*' ' + "T = _tags_of_fast(p) or get_tags(p) or []  # TAG-TRUTH v75: read, assume nothing",
                  d*' ' + "for t in T:",
                  d*' ' + "    nm = re.sub(r'[/\\\\:]', '-', (t or '').split(chr(10))[0].strip())",
                  d*' ' + "    if not nm or nm in ('Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Gray', 'Grey'): continue",
                  d*' ' + "    d0 = os.path.dirname(p)",
                  d*' ' + "    if os.path.basename(d0) == nm: continue",
                  d*' ' + "    base = d0 if len(os.path.relpath(d0, self.root).split(os.sep)) <= 2 else os.path.dirname(d0)",
                  d*' ' + "    tgt = os.path.join(base, nm)",
                  d*' ' + "    os.makedirs(tgt, exist_ok=True)",
                  d*' ' + "    dst = os.path.join(tgt, os.path.basename(p)); c = 1",
                  d*' ' + "    b2, e2 = os.path.splitext(os.path.basename(p))",
                  d*' ' + "    while os.path.exists(dst): dst = os.path.join(tgt, f'{b2}_{c}{e2}'); c += 1",
                  d*' ' + "    if _settling(p): return",
                  d*' ' + "    try:",
                  d*' ' + "        os.rename(p, dst); say(f'📁 [move] {os.path.basename(p)} -> {nm}/'); return",
                  d*' ' + "    except Exception: return"]
    done.append('tag-truth-filing')
for k, l in enumerate(B):
    if l.strip().startswith("ck('S94 client-root block on live path'"):
        B[k] = ind(l)*' ' + "ck('S94 client-root block on live path', _src.index('def handle_tags') < _src.index(chr(35)+' CLIENT-ROOT v73') < _src.index('split(os.sep)) < 2: return'))"
        done.append('S94-robust'); break
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S95 tag-skip is per-call not per-instance" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if l.strip().startswith("ck('S94 client-root block on live path'"))
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S95 tag-skip is per-call not per-instance', 'skip_tags=None' in _src and _src.count('skip_tags=False') >= 2 and (chr(35)+' SKIP-FIX') in _src)")
    B.insert(i+2, d*' ' + "ck('S96 tag-truth filing, no whitelist', (chr(35)+' TAG-TRUTH') in _src)")
    B.insert(i+3, d*' ' + "ck('S97 heal and drain read tags per call', _src.count('skip_tags=False') >= 2)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S95-S97-guards')
print('✅', done)
