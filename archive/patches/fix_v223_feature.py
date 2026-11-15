import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if '# WORKSPACE-CLAMP v81.82' not in srcg:
    i = next(k for k, l in enumerate(g) if l.strip().startswith('_qt = [t for t in q.split()]'))
    d = ind(g[i])
    g[i:i] = [d*' ' + "_cr = os.path.dirname(os.path.dirname(f['path']))  # WORKSPACE-CLAMP v81.82: the butler's world is the workspace root; nothing above it is ever walked",
              d*' ' + "_roots = [f['path']] + ([_cr] if (_cr.startswith(root) and _cr != f['path']) else [])"]
    done.append('workspace-clamp')
    srcg = '\n'.join(g)
if 'for _sr2 in _roots:' not in srcg:
    g = srcg.split('\n')
    for k, l in enumerate(g):
        if "for _sr2 in [f['path'], os.path.dirname(os.path.dirname(f['path']))]:" in l:
            g[k] = ind(l)*' ' + "for _sr2 in _roots:"
            done.append('strict-clamp'); break
    srcg = '\n'.join(g)
if '([] if hit else _roots)' not in srcg:
    g = srcg.split('\n')
    for k, l in enumerate(g):
        if "for _sr in ([] if hit else [f['path'], os.path.dirname(os.path.dirname(f['path']))]):" in l:
            g[k] = ind(l)*' ' + "for _sr in ([] if hit else _roots):"
            done.append('loose-clamp'); break
    srcg = '\n'.join(g)
if '# PICK-GRACEFUL-WIDE v81.82' not in srcg:
    g = srcg.split('\n')
    i_say = next(k for k, l in enumerate(g) if 'pick the human by email' in l and l.strip().startswith('say('))
    i_try = next(k for k in range(i_say, len(g)) if g[k].strip().startswith("try: hit = _strict[int(input("))
    d = ind(g[i_say])
    g.insert(i_say, d*' ' + "try:  # PICK-GRACEFUL-WIDE v81.82: Ctrl-C anywhere in the picker - listing or prompt - is a choice, not a crash")
    for j in range(i_say + 1, i_try + 2):
        if g[j].strip(): g[j] = '    ' + g[j]
    done.append('pick-graceful-wide')
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
def anch(*needles):
    for n in needles:
        hit = [k for k, l in enumerate(B) if n in l]
        if hit: return hit[-1]
    return None
GU = [("'S189 the butler's world is the workspace, nothing above", "'S188 Ctrl-C at the picker is a choice, not a crash", "ck('S189 the butler'+chr(39)+'s world is the workspace, nothing above', (chr(35)+' WORKSPACE-CLAMP v81.82') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and 'for _sr in ([] if hit else _roots)' in open(os.path.join(BASE_DIR, 'briefing.py')).read())"),
      ("'S190 Ctrl-C anywhere in the picker is graceful", "'S189 the butler's world is the workspace, nothing above", "ck('S190 Ctrl-C anywhere in the picker is graceful', (chr(35)+' PICK-GRACEFUL-WIDE v81.82') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")]
for needle, fb, line in GU:
    if needle not in '\n'.join(B):
        i = anch(needle, fb)
        d = ind(B[i])
        B.insert(i+1, d*' ' + line)
        done.append(needle.split()[0].strip("'") + '-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
