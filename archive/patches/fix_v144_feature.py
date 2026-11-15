import ast
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# REPL-GATE v81.12' not in src:
    i = next(k for k, l in enumerate(B) if l.strip() == 'if sys.stdin.isatty():')
    B[i] = ind(B[i])*' ' + 'if INTERACTIVE:  # REPL-GATE v81.12: only a real terminal gets the REPL; a log-file stdout walks to the watcher'
    done.append('repl-gate-exact')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S119 the REPL door keys on INTERACTIVE" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S118 the REPL cannot park or kill the loop" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S119 the REPL door keys on INTERACTIVE', (chr(35)+' REPL-GATE v81.12') in _src and ('if sys.stdin' + '.isatty():') not in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S119-guard')
print('✅', done)
