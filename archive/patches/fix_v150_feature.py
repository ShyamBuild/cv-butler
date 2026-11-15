import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
n = 0
for k, l in enumerate(B):
    if '_t.time()' in l or '_t.sleep(' in l:
        B[k] = l.replace('_t.time()', 'time.time()').replace('_t.sleep(', 'time.sleep('); n += 1
if n: done.append(f'clock-globalized-x{n}')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
for k, l in enumerate(B):
    if l.strip().startswith("ck('S111 pulse clock uses the file own alias'") or l.strip().startswith("ck('S111 pulse clock uses the file's own alias'"):
        B[k] = ind(l)*' ' + "ck('S111 pulse clock uses the module global clock', ('_t' + '.time()') not in _src and 'import time' in _src)"
        done.append('S111-rewritten'); break
if "'S123 no ghost clock alias" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S122 exactly one late pulse start" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S123 no ghost clock alias', ('_t' + '.time()') not in _src and ('_t' + '.sleep(') not in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S123-guard')
print('✅', done)
