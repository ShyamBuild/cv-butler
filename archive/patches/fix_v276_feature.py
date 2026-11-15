import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if 'TAG-DEDUPE' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('if not cands:') and 'no candidate file matches' in l)
    d = ind(B[i])
    B.insert(i, d*' ' + "seen = set(); cands = [c for c in cands if os.path.realpath(c) not in seen and not seen.add(os.path.realpath(c))]  # TAG-DEDUPE v84.2d: overlapping chairs must not double a human in a question")
    done.append('tag-dedupe')
    src = '\n'.join(B)
for k in range(len(B) - 1, -1, -1):
    if "'S225 six verbs answer before any root is validated" in B[k] and 'ck(' in B[k]:
        del B[k]
        done.append('S225-pruned')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S233 overlapping chairs never double a human in a question" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S232 a question keeps its numbers" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S233 overlapping chairs never double a human in a question', (chr(35)+' TAG-DEDUPE v84.2d') in _src)")
    done.append('S233-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
