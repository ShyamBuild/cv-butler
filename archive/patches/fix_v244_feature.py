import ast, os
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
if "'S203 the autodraft sleep-switch honours the off word" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S202 the door is asked until it answers" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S203 the autodraft sleep-switch honours the off word', ('if st == ' + chr(39) + 'off' + chr(39) + ': return False') in _src and ('if not self._ad_enabled' + '():') in _src)  # S203: the mute switch stays wired - a refactor may move it but may not delete it")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S203-guard')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
print('✅', done)
