import ast, os
done = []
F = open('briefing.py').read().split('\n')
if F.count('def _pick_model(') == 2:
    i = next(k for k, l in enumerate(F) if l.strip().startswith('def _pick_model('))
    j = next(k for k, l in enumerate(F) if l.strip().startswith('def _company_root('))
    del F[i:j]
    done.append('briefing-dedupe')
new = '\n'.join(F); ast.parse(new); open('briefing.py', 'w').write(new)
B = open('butler.py').read().split('\n')
if 'LOG-TRIM v51' not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if 'if _git_stamp() != GIT_STAMP:' in l)
    d = len(B[i]) - len(B[i].lstrip())
    B[i:i] = [d*' ' + 'try:',
              d*' ' + '    # LOG-TRIM v51',
              d*' ' + "    _lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'butler_live.log')",
              d*' ' + '    if os.path.exists(_lp) and os.path.getsize(_lp) > 5_000_000:',
              d*' ' + "        open(_lp, 'w').write(open(_lp, errors='ignore').read()[-500_000:])",
              d*' ' + 'except Exception:',
              d*' ' + '    pass']
    done.append('log-trim')
if "'S56 log trim + single helper defs" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S55 scenario templates" in l)
    d = len(B[i]) - len(B[i].lstrip())
    B.insert(i+1, d*' ' + "ck('S56 log trim + single helper defs', (chr(35) + ' LOG-TRIM') in _src and _br.count('def _pick_model(') == 1)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S56-guard')
else:
    open('butler.py', 'w').write('\n'.join(B))
G = open('.gitignore').read() if os.path.exists('.gitignore') else ''
add = [x for x in ('archive/', '*.log') if x not in G.splitlines()]
if add:
    open('.gitignore', 'a').write('\n' + '\n'.join(add) + '\n'); done.append('gitignore-' + '+'.join(add))
print('✅', done)
