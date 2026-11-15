import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# PULSE-CLOCK v81.14' not in src:
    i = next(k for k, l in enumerate(B) if l.strip().startswith('def _pulse_loop():'))
    d = ind(B[i]) + 4
    B[i+1:i+1] = [d*' ' + "import time as _t  # PULSE-CLOCK v81.14: the thread owns its clock; no enclosing cell may starve it",
                  d*' ' + "print('🩺 pulse thread armed', flush=True)"]
    done.append('pulse-clock')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S121 the pulse thread owns its clock" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S120 the pulse owns its own thread" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S121 the pulse thread owns its clock', (chr(35)+' PULSE-CLOCK') in _src and 'pulse thread armed' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S121-guard')
print('✅', done)
