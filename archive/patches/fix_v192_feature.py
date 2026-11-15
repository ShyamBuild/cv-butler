import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if "'S166 the butler never removes a directory" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S165 main never speaks self" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S166 the butler never removes a directory', 'rmtree' not in _src and 'rmdir(' not in _src and 'shutil.rmtree' not in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S166-guard')
src = '\n'.join(B); ast.parse(src)
print('✅', done)
