import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
i = next(k for k, l in enumerate(B) if l.strip() == 'def _tag_poll(self):')
j = next(k for k in range(i, i+45) if B[k].strip() == 'return changed')
n1 = 0
for k in range(i, j+1):
    if 'time.time()' in B[k]: B[k] = B[k].replace('time.time()', '_t.time()'); n1 += 1
if n1: done.append(f'tag-poll-time-fix-x{n1}')
a = next(k for k, l in enumerate(B) if l.strip().startswith('def _ad_enabled(self):'))
b = next(k for k in range(a, a+140) if B[k].strip().startswith('def _heal(self, say=print):'))
n2 = 0
for k in range(a, b):
    if 'time.time()' in B[k]: B[k] = B[k].replace('time.time()', '_t.time()'); n2 += 1
if n2: done.append(f'autodraft-time-fix-x{n2}')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S111 pulse clock uses the file's own alias" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S110 autodraft log reachable from chat" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S111 pulse clock uses the file own alias', _src.split('def _tag_poll')[1].split('return changed')[0].count('time.time()') == 0 and _src.split('def _ad_enabled')[1].split('def _heal')[0].count('time.time()') == 0)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S111-guard')
print('✅', done)
