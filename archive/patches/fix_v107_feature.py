import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
B = [l for l in B if l.strip() != 'B._snapshot(hsay)']
i = max(k for k, l in enumerate(B) if 'B._heal(hsay)' in l)
B[i+1:i+1] = [ind(B[i])*' ' + 'try: B._snapshot(hsay)  # SNAPSHOT-CALL v69.1',
              ind(B[i])*' ' + 'except Exception: pass']
done.append('snapshot-relocated')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S87 snapshot call lives in heartbeat" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S86 cloud snapshot habit" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S87 snapshot call lives in heartbeat', _src.count('B._snapshot(hsay)') == 1 and _src.rindex('B._snapshot(hsay)') > _src.rindex('B._heal(hsay)'))")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S87-guard')
print('✅', done)
