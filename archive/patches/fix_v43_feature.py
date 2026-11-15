import ast
p = 'butler.py'; L = open(p).read().split('\n'); done = []
if '⛔ refused' not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if l.strip().startswith('with open(lock_path, "w")'))
    d = len(l0 := L[i]) - len(l0.lstrip())
    blk = [d*' ' + 'for _fn in os.listdir(os.path.dirname(lock_path)):',
           d*' ' + "    if not (_fn.startswith('butler_') and _fn.endswith('.lock')): continue",
           d*' ' + '    _lp = os.path.join(os.path.dirname(lock_path), _fn)',
           d*' ' + '    if _lp == lock_path: continue',
           d*' ' + '    try:',
           d*' ' + "        _pid, _rt = open(_lp).read().strip().split('|', 1)",
           d*' ' + '    except Exception:',
           d*' ' + '        continue',
           d*' ' + '    if not _alive(_lp): continue',
           d*' ' + "    _a = root.rstrip('/') + '/'; _b = _rt.rstrip('/') + '/'",
           d*' ' + '    if _rt != root and (_a.startswith(_b) or _b.startswith(_a)):',
           d*' ' + '        print(f"⛔ refused: live butler {_pid} already covers {_rt} (one writer per tree) - use chat/CLI one-shots, not a second console")',
           d*' ' + '        sys.exit(0)']
    L[i:i] = blk
    done.append('containment-refusal')
if "'S25 containment" not in '\n'.join(L):
    i = next(k for k, l in enumerate(L) if "'S24 live locks visible" in l)
    d = len(L[i]) - len(L[i].lstrip())
    L.insert(i+1, d*' ' + "ck('S25 containment refusal at lock acquire', ('\\u26d4' + ' refused: live butler') in _src)")
    done.append('S25-guard')
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
print('✅', done or 'nothing missing')
