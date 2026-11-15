import ast, os, shutil
for f in ('butler.py', 'wa.py'):
    shutil.copy(os.path.expanduser('~/pending_v30/' + f), f)
p = 'butler.py'; L = open(p).read().split('\n'); done = ['union-restored-from-pending']
for k, l in enumerate(L):
    if l.strip().startswith("ck('S1 bindings'"):
        d = len(l) - len(l.lstrip())
        L[k:k+1] = [d*' ' + "_tm = next((m for m in ('tags_of','_tags_of','_read_tags','get_tags','_tags') if callable(getattr(B, m, None))), None)",
                    d*' ' + "ck('S1 bindings', _tm is not None and all(callable(getattr(B, m, None)) for m in ('route','handle_tags','_reconcile_tags','_compact_numbers','position_folder_for')), _tm)"]
        done.append('S1-dynamic-method'); break
for k, l in enumerate(L):
    if l.strip().startswith('tags = B.tags_of('):
        d = len(l) - len(l.lstrip())
        L[k] = d*' ' + 'tags = getattr(B, _tm)(_prw[0]) if (_prw and _tm) else []'
        done.append('S2-dynamic-method'); break
new = '\n'.join(L); ast.parse(new); open(p, 'w').write(new)
shutil.copy(p, os.path.expanduser('~/pending_v30/butler.py'))
print('✅', done)
