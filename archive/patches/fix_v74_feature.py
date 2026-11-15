import ast, os
done = []
L = open('briefing.py').read().split('\n')
src = '\n'.join(L)
if src.count('def _pick_model(') == 2:
    i = next(k for k, l in enumerate(L) if l.strip().startswith('def _pick_model('))
    j = next(k for k, l in enumerate(L) if l.strip().startswith('def _company_root('))
    del L[i:j]
    done.append('briefing-dedupe')
new = '\n'.join(L); ast.parse(new); open('briefing.py', 'w').write(new)
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
    done.append('S56-guard')
open('butler.py', 'w').write('\n'.join(B))
print('✅', done)
