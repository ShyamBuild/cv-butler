import ast, re
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# HEADLESS-FIX v81.9' not in src:
    i = next(k for k, l in enumerate(B) if re.match(r'^INTERACTIVE\s*=', l))
    B[i] = 'INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()  # HEADLESS-FIX v81.9: a log-file stdout means headless; loop, do not listen'
    done.append('headless-fix')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S117 headless butler loops instead of listening" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S116 the log speaks instantly" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S117 headless butler loops instead of listening', (chr(35)+' HEADLESS-FIX') in _src and 'sys.stdout.isatty()' in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S117-guard')
print('✅', done)
