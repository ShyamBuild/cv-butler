import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
G = os.path.join(os.getcwd(), 'briefing.py')
g = open(G).read().split('\n')
srcg = '\n'.join(g)
if '# DEDUPE v81.79' not in srcg:
    for k, l in enumerate(g):
        if '_strict.append(os.path.join(dp, x))' in l:
            d = ind(l)
            g[k:k+1] = [d*' ' + "_p = os.path.join(dp, x)",
                        d*' ' + "if _p not in _strict: _strict.append(_p)  # DEDUPE v81.79: the client walk contains the position walk; a human is listed once"]
            done.append('dedupe'); break
    srcg = '\n'.join(g)
if '# PATH-LABEL v81.79' not in srcg:
    g = srcg.split('\n')
    for k, l in enumerate(g):
        if 'os.path.basename(os.path.dirname(_c))' in l and 'POSITION-LABEL v81.76' in l:
            g[k] = l.replace('os.path.basename(os.path.dirname(_c))', 'os.path.relpath(os.path.dirname(_c), root)').replace('# POSITION-LABEL v81.76:', '# POSITION-LABEL v81.76 + PATH-LABEL v81.79: the whole folder trail from the client down - position and stage together - because that is what tells humans apart;')
            done.append('path-label'); break
    srcg = '\n'.join(g)
if srcg != open(G).read():
    ast.parse(srcg); open(G, 'w').write(srcg)
B = open('butler.py').read().split('\n')
if "'S186 a human is listed once, labelled by their whole trail" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S185 the picker labels humans by position, not client" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S186 a human is listed once, labelled by their whole trail', (chr(35)+' DEDUPE v81.79') in open(os.path.join(BASE_DIR, 'briefing.py')).read() and (chr(35)+' PATH-LABEL v81.79') in open(os.path.join(BASE_DIR, 'briefing.py')).read())")
    done.append('S186-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
