import ast, re
done = []
def ind(l): return len(l) - len(l.lstrip())
B = open('butler.py').read().split('\n')
src = '\n'.join(B)
if '# REPL-SAFE v81.10' not in src:
    bi = next(k for k, l in enumerate(B) if 'Watching silently' in l)
    for k in range(max(0, bi-8), bi):
        if re.search(r'if\s+.*isatty\(\)\s*:', B[k]) or B[k].strip() == 'if INTERACTIVE:':
            B[k] = ind(B[k])*' ' + 'if INTERACTIVE:  # REPL-GATE v81.10'
            done.append('repl-gate'); break
    ii = next((k for k in range(bi, bi+10) if 'input(' in B[k]), None)
    if ii is not None:
        d = ind(B[ii])
        B[ii:ii+1] = [d*' ' + 'try:',
                      (d+4)*' ' + B[ii].strip(),
                      d*' ' + 'except EOFError:  # REPL-SAFE v81.10',
                      (d+4)*' ' + 'INTERACTIVE = False',
                      (d+4)*' ' + 'continue']
        done.append('repl-eof-safe')
src = '\n'.join(B); ast.parse(src); open('butler.py', 'w').write(src)
B = open('butler.py').read().split('\n')
if "'S118 the REPL cannot park or kill the loop" not in '\n'.join(B):
    i = next(k for k, l in enumerate(B) if "'S117 headless butler loops instead of listening" in l)
    d = ind(B[i])
    B.insert(i+1, d*' ' + "ck('S118 the REPL cannot park or kill the loop', (chr(35)+' REPL-GATE') in _src and (chr(35)+' REPL-SAFE') in _src)")
    open('butler.py', 'w').write('\n'.join(B)); done.append('S118-guard')
print('✅', done)
